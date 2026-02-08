#!/usr/bin/env python3
"""
Bend Logger - Sistema de Auditoria e Confiabilidade de Dobras
==============================================================

PROPÓSITO:
- Registra CADA operação de dobra com timestamps
- Compara ângulo PROGRAMADO vs ângulo EXECUTADO
- Detecta discrepâncias e alerta o operador
- Calcula compensação sugerida baseado no histórico
- Identifica padrões de erro (por velocidade, temperatura, etc.)

Data: 08/Fev/2026
Autor: Eng. Lucas William Junges
"""

import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics


@dataclass
class BendRecord:
    """Registro de uma operação de dobra"""
    timestamp: str           # ISO format
    bend_number: int         # 1, 2, ou 3
    angle_programmed: float  # Ângulo que o operador digitou
    angle_executed: float    # Ângulo real medido pelo encoder
    error_degrees: float     # Diferença (executado - programado)
    speed_rpm: float         # Velocidade no momento da dobra
    direction: str           # 'CCW' ou 'CW'
    duration_ms: int         # Tempo de execução em ms
    success: bool            # Se a dobra foi considerada bem-sucedida
    piece_count: int         # Número da peça produzida


class BendLogger:
    """
    Sistema de log e auditoria de operações de dobra.

    Funcionalidades:
    - Registra cada dobra em arquivo JSON rotativo
    - Calcula estatísticas de erro
    - Sugere compensação baseada no histórico
    - Alerta quando erro excede tolerância
    """

    # Tolerância padrão em graus (erro aceitável)
    DEFAULT_TOLERANCE = 2.0  # ±2 graus

    # Máximo de registros em memória antes de salvar
    FLUSH_THRESHOLD = 10

    # Diretório de logs
    LOG_DIR = Path(__file__).parent / 'logs'

    def __init__(self, tolerance: float = DEFAULT_TOLERANCE):
        """
        Inicializa o logger.

        Args:
            tolerance: Tolerância de erro em graus (padrão ±2°)
        """
        self.tolerance = tolerance
        self.records: List[BendRecord] = []
        self.session_start = datetime.now()
        self.current_piece = 0

        # Estatísticas da sessão
        self.session_stats = {
            'total_bends': 0,
            'successful_bends': 0,
            'error_sum': 0.0,
            'errors': [],  # Lista de erros para cálculo de desvio padrão
            'max_error': 0.0,
            'alerts': 0,
        }

        # Cria diretório de logs se não existir
        self.LOG_DIR.mkdir(exist_ok=True)

        # Carrega histórico recente para cálculo de compensação
        self.history = self._load_recent_history()

        print(f"📊 BendLogger iniciado (tolerância: ±{tolerance}°)")
        print(f"   Histórico: {len(self.history)} registros anteriores")

    def _load_recent_history(self, max_records: int = 100) -> List[BendRecord]:
        """
        Carrega histórico recente de arquivos de log.

        Args:
            max_records: Máximo de registros a carregar

        Returns:
            Lista de registros anteriores
        """
        history = []

        try:
            # Lista arquivos de log ordenados por data (mais recente primeiro)
            log_files = sorted(
                self.LOG_DIR.glob('bends_*.json'),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )

            for log_file in log_files[:5]:  # Últimos 5 arquivos
                with open(log_file, 'r') as f:
                    records = json.load(f)
                    for r in records:
                        if len(history) >= max_records:
                            break
                        history.append(BendRecord(**r))

        except Exception as e:
            print(f"⚠️ Erro carregando histórico: {e}")

        return history

    def log_bend(
        self,
        bend_number: int,
        angle_programmed: float,
        angle_executed: float,
        speed_rpm: float,
        direction: str = 'CCW',
        duration_ms: int = 0
    ) -> Dict[str, Any]:
        """
        Registra uma operação de dobra.

        Args:
            bend_number: Número da dobra (1, 2, 3)
            angle_programmed: Ângulo que foi programado
            angle_executed: Ângulo real medido pelo encoder
            speed_rpm: Velocidade do motor
            direction: Direção de rotação
            duration_ms: Duração da operação

        Returns:
            Dicionário com resultado da análise:
            {
                'success': bool,
                'error': float,
                'alert': str ou None,
                'compensation_suggested': float,
            }
        """
        # Calcula erro
        error = angle_executed - angle_programmed
        abs_error = abs(error)
        success = abs_error <= self.tolerance

        # Incrementa contador de peças
        if bend_number == 1:
            self.current_piece += 1

        # Cria registro
        record = BendRecord(
            timestamp=datetime.now().isoformat(),
            bend_number=bend_number,
            angle_programmed=angle_programmed,
            angle_executed=angle_executed,
            error_degrees=error,
            speed_rpm=speed_rpm,
            direction=direction,
            duration_ms=duration_ms,
            success=success,
            piece_count=self.current_piece
        )

        # Adiciona aos registros
        self.records.append(record)
        self.history.append(record)

        # Atualiza estatísticas
        self.session_stats['total_bends'] += 1
        self.session_stats['error_sum'] += abs_error
        self.session_stats['errors'].append(error)

        if success:
            self.session_stats['successful_bends'] += 1

        if abs_error > self.session_stats['max_error']:
            self.session_stats['max_error'] = abs_error

        # Gera alerta se erro exceder tolerância
        alert = None
        if not success:
            self.session_stats['alerts'] += 1
            if error > 0:
                alert = f"⚠️ DOBRA {bend_number} PASSOU {abs_error:.1f}° do alvo!"
            else:
                alert = f"⚠️ DOBRA {bend_number} FICOU {abs_error:.1f}° ANTES do alvo!"
            print(alert)

        # Calcula compensação sugerida baseada no histórico
        compensation = self._calculate_suggested_compensation(bend_number, speed_rpm)

        # Flush se atingir threshold
        if len(self.records) >= self.FLUSH_THRESHOLD:
            self._flush_to_disk()

        # Log
        status = "✅" if success else "❌"
        print(f"{status} Dobra {bend_number}: prog={angle_programmed:.1f}° exec={angle_executed:.1f}° erro={error:+.1f}°")

        return {
            'success': success,
            'error': error,
            'alert': alert,
            'compensation_suggested': compensation,
            'record': asdict(record)
        }

    def _calculate_suggested_compensation(
        self,
        bend_number: int,
        speed_rpm: float,
        lookback: int = 20
    ) -> float:
        """
        Calcula compensação sugerida baseada no histórico de erros.

        A compensação é o oposto da média dos erros recentes.
        Se a máquina está consistentemente passando +3°, sugere -3°.

        Args:
            bend_number: Número da dobra
            speed_rpm: Velocidade atual
            lookback: Quantos registros anteriores considerar

        Returns:
            Compensação sugerida em graus (negativo = reduzir ângulo programado)
        """
        # Filtra registros relevantes (mesma dobra, velocidade similar)
        relevant = [
            r for r in self.history[-lookback:]
            if r.bend_number == bend_number
            and abs(r.speed_rpm - speed_rpm) < 3  # Tolerância de velocidade
        ]

        if len(relevant) < 3:
            return 0.0  # Dados insuficientes

        # Calcula média dos erros
        errors = [r.error_degrees for r in relevant]
        mean_error = statistics.mean(errors)

        # Compensação é o oposto do erro médio
        compensation = -mean_error

        # Arredonda para 0.5 graus
        compensation = round(compensation * 2) / 2

        return compensation

    def get_compensation_recommendation(self) -> Dict[str, float]:
        """
        Retorna recomendações de compensação para cada dobra/velocidade.

        Returns:
            Dicionário com compensações sugeridas por cenário
        """
        recommendations = {}

        for bend in [1, 2, 3]:
            for speed in [5, 10, 15]:
                key = f"bend_{bend}_speed_{speed}"
                comp = self._calculate_suggested_compensation(bend, speed)
                if comp != 0:
                    recommendations[key] = comp

        return recommendations

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da sessão atual.

        Returns:
            Dicionário com estatísticas
        """
        stats = self.session_stats.copy()

        if stats['total_bends'] > 0:
            stats['avg_error'] = stats['error_sum'] / stats['total_bends']
            stats['success_rate'] = (stats['successful_bends'] / stats['total_bends']) * 100

            if len(stats['errors']) >= 2:
                stats['std_dev'] = statistics.stdev(stats['errors'])
            else:
                stats['std_dev'] = 0.0
        else:
            stats['avg_error'] = 0.0
            stats['success_rate'] = 100.0
            stats['std_dev'] = 0.0

        stats['session_duration'] = str(datetime.now() - self.session_start)
        stats['pieces_produced'] = self.current_piece

        # Remove lista de erros do retorno (muito grande)
        del stats['errors']

        return stats

    def _flush_to_disk(self):
        """Salva registros em memória para disco."""
        if not self.records:
            return

        try:
            # Nome do arquivo com data
            date_str = datetime.now().strftime('%Y%m%d')
            filename = self.LOG_DIR / f'bends_{date_str}.json'

            # Carrega registros existentes se houver
            existing = []
            if filename.exists():
                with open(filename, 'r') as f:
                    existing = json.load(f)

            # Adiciona novos registros
            new_records = [asdict(r) for r in self.records]
            all_records = existing + new_records

            # Salva
            with open(filename, 'w') as f:
                json.dump(all_records, f, indent=2)

            print(f"💾 {len(self.records)} registros salvos em {filename.name}")

            # Limpa memória
            self.records = []

        except Exception as e:
            print(f"❌ Erro salvando logs: {e}")

    def check_consistency(
        self,
        angle_programmed: float,
        angle_executed: float,
        bend_number: int
    ) -> Dict[str, Any]:
        """
        Verifica consistência de uma dobra sem registrar.

        Útil para verificação em tempo real durante a dobra.

        Args:
            angle_programmed: Ângulo programado
            angle_executed: Ângulo atual do encoder
            bend_number: Número da dobra

        Returns:
            Status de consistência
        """
        error = angle_executed - angle_programmed
        abs_error = abs(error)

        status = 'OK'
        message = None

        if abs_error > self.tolerance * 3:
            status = 'CRITICAL'
            message = f"ERRO CRÍTICO: {abs_error:.1f}° de discrepância!"
        elif abs_error > self.tolerance * 2:
            status = 'WARNING'
            message = f"Aviso: {abs_error:.1f}° de desvio"
        elif abs_error > self.tolerance:
            status = 'MINOR'
            message = f"Desvio menor: {abs_error:.1f}°"

        return {
            'status': status,
            'error': error,
            'within_tolerance': abs_error <= self.tolerance,
            'message': message
        }

    def get_error_trend(self, lookback: int = 10) -> Dict[str, Any]:
        """
        Analisa tendência de erro nas últimas dobras.

        Returns:
            Análise de tendência (melhorando, piorando, estável)
        """
        if len(self.history) < lookback:
            return {'trend': 'INSUFFICIENT_DATA', 'samples': len(self.history)}

        recent = self.history[-lookback:]
        errors = [abs(r.error_degrees) for r in recent]

        # Divide em duas metades
        first_half = errors[:len(errors)//2]
        second_half = errors[len(errors)//2:]

        avg_first = statistics.mean(first_half) if first_half else 0
        avg_second = statistics.mean(second_half) if second_half else 0

        if avg_second < avg_first * 0.8:
            trend = 'IMPROVING'
            message = f"Erro diminuindo: {avg_first:.1f}° → {avg_second:.1f}°"
        elif avg_second > avg_first * 1.2:
            trend = 'WORSENING'
            message = f"⚠️ Erro aumentando: {avg_first:.1f}° → {avg_second:.1f}°"
        else:
            trend = 'STABLE'
            message = f"Erro estável: ~{avg_second:.1f}°"

        return {
            'trend': trend,
            'message': message,
            'avg_error_recent': avg_second,
            'avg_error_previous': avg_first
        }

    def close(self):
        """Fecha o logger, salvando registros pendentes."""
        self._flush_to_disk()

        # Salva resumo da sessão
        stats = self.get_session_stats()
        print("\n📊 RESUMO DA SESSÃO:")
        print(f"   Total de dobras: {stats['total_bends']}")
        print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
        print(f"   Erro médio: {stats['avg_error']:.2f}°")
        print(f"   Erro máximo: {stats['max_error']:.2f}°")
        print(f"   Desvio padrão: {stats['std_dev']:.2f}°")
        print(f"   Peças produzidas: {stats['pieces_produced']}")
        print(f"   Alertas emitidos: {stats['alerts']}")


# Singleton global
_bend_logger: Optional[BendLogger] = None


def get_bend_logger(tolerance: float = BendLogger.DEFAULT_TOLERANCE) -> BendLogger:
    """
    Retorna instância singleton do BendLogger.

    Args:
        tolerance: Tolerância em graus (só usado na primeira chamada)

    Returns:
        Instância do BendLogger
    """
    global _bend_logger

    if _bend_logger is None:
        _bend_logger = BendLogger(tolerance)

    return _bend_logger


if __name__ == '__main__':
    # Teste do logger
    print("=== TESTE DO BEND LOGGER ===\n")

    logger = BendLogger(tolerance=2.0)

    # Simula algumas dobras
    test_data = [
        # (bend, programado, executado, velocidade)
        (1, 90.0, 92.5, 15),   # Erro +2.5° (fora da tolerância)
        (2, 45.0, 46.0, 15),   # Erro +1.0° (OK)
        (3, 30.0, 31.5, 15),   # Erro +1.5° (OK)
        (1, 90.0, 91.0, 10),   # Erro +1.0° (OK)
        (2, 45.0, 44.5, 10),   # Erro -0.5° (OK)
        (3, 30.0, 33.0, 10),   # Erro +3.0° (fora da tolerância)
        (1, 90.0, 90.5, 5),    # Erro +0.5° (OK)
        (2, 45.0, 45.2, 5),    # Erro +0.2° (OK)
        (3, 30.0, 30.1, 5),    # Erro +0.1° (OK)
    ]

    for bend, prog, exec, speed in test_data:
        result = logger.log_bend(
            bend_number=bend,
            angle_programmed=prog,
            angle_executed=exec,
            speed_rpm=speed,
            direction='CCW',
            duration_ms=1500
        )
        print(f"   Compensação sugerida: {result['compensation_suggested']:+.1f}°\n")

    # Mostra estatísticas
    print("\n" + "="*50)
    stats = logger.get_session_stats()
    print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
    print(f"Erro médio: {stats['avg_error']:.2f}°")

    # Mostra recomendações
    print("\n" + "="*50)
    print("RECOMENDAÇÕES DE COMPENSAÇÃO:")
    recs = logger.get_compensation_recommendation()
    for key, val in recs.items():
        print(f"   {key}: {val:+.1f}°")

    # Tendência
    trend = logger.get_error_trend()
    print(f"\nTendência: {trend['trend']} - {trend.get('message', '')}")

    logger.close()
