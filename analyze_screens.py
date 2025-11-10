#!/usr/bin/env python3
"""
Analisa o arquivo Screen.dbf para extrair o mapeamento completo de telas da IHM
"""

import struct
import json
from datetime import datetime

def read_dbf(filepath):
    """
    Lê arquivo DBF e retorna lista de registros
    """
    with open(filepath, 'rb') as f:
        # Header DBF
        header = f.read(32)

        # Byte 0: Tipo de arquivo
        file_type = header[0]

        # Bytes 1-3: Data da última atualização
        year = header[1] + 1900
        month = header[2]
        day = header[3]

        # Bytes 4-7: Número de registros (little-endian)
        num_records = struct.unpack('<I', header[4:8])[0]

        # Bytes 8-9: Tamanho do header (little-endian)
        header_size = struct.unpack('<H', header[8:10])[0]

        # Bytes 10-11: Tamanho de cada registro (little-endian)
        record_size = struct.unpack('<H', header[10:12])[0]

        print(f"📊 Análise do DBF:")
        print(f"  Tipo: {hex(file_type)}")
        print(f"  Última atualização: {day:02d}/{month:02d}/{year}")
        print(f"  Número de registros: {num_records}")
        print(f"  Tamanho do header: {header_size} bytes")
        print(f"  Tamanho do registro: {record_size} bytes")
        print()

        # Ler field descriptors (32 bytes cada)
        fields = []
        field_start = 32

        while True:
            f.seek(field_start)
            field_header = f.read(32)

            # 0x0D marca fim dos field descriptors
            if field_header[0] == 0x0D:
                break

            # Nome do campo (bytes 0-10, null-terminated)
            field_name = field_header[0:11].decode('ascii', errors='ignore').strip('\x00')

            # Tipo do campo (byte 11)
            field_type = chr(field_header[11])

            # Tamanho do campo (byte 16)
            field_length = field_header[16]

            # Casas decimais (byte 17)
            field_decimals = field_header[17]

            fields.append({
                'name': field_name,
                'type': field_type,
                'length': field_length,
                'decimals': field_decimals
            })

            field_start += 32

        print(f"🔍 Campos encontrados ({len(fields)}):")
        for i, field in enumerate(fields):
            print(f"  {i+1}. {field['name']:12s} - Tipo: {field['type']}, Tamanho: {field['length']}, Decimais: {field['decimals']}")
        print()

        # Ler registros
        f.seek(header_size)
        records = []

        for rec_num in range(num_records):
            record_data = f.read(record_size)

            # Byte 0: deletion flag
            deleted = record_data[0] == 0x2A  # '*' = deleted

            if deleted:
                continue

            # Parse campos
            record = {}
            offset = 1  # Pula deletion flag

            for field in fields:
                field_data = record_data[offset:offset + field['length']]

                if field['type'] == 'C':  # Character
                    value = field_data.decode('latin-1', errors='ignore').strip()
                elif field['type'] == 'N':  # Numeric
                    value_str = field_data.decode('ascii', errors='ignore').strip()
                    try:
                        if field['decimals'] > 0:
                            value = float(value_str) if value_str else 0.0
                        else:
                            value = int(value_str) if value_str else 0
                    except ValueError:
                        value = 0
                elif field['type'] == 'L':  # Logical
                    value = field_data[0] in (ord('T'), ord('t'), ord('Y'), ord('y'))
                elif field['type'] == 'D':  # Date
                    date_str = field_data.decode('ascii', errors='ignore')
                    value = date_str if date_str.strip() else None
                elif field['type'] == 'M':  # Memo
                    value = field_data.decode('latin-1', errors='ignore').strip()
                else:
                    value = field_data

                record[field['name']] = value
                offset += field['length']

            records.append(record)

        return records, fields


def analyze_screens(records):
    """
    Analisa registros de telas e extrai informações relevantes
    """
    print(f"\n📺 Telas encontradas: {len(records)}\n")

    screens_map = {}

    for i, rec in enumerate(records):
        print(f"─── Tela {i} ───")
        for key, value in rec.items():
            if value and str(value).strip():
                print(f"  {key:15s}: {value}")
        print()

        # Criar mapeamento estruturado
        screens_map[i] = rec

    return screens_map


if __name__ == '__main__':
    import sys

    dbf_path = 'ladder_extract/Screen.dbf'

    if len(sys.argv) > 1:
        dbf_path = sys.argv[1]

    print(f"🔧 Analisando: {dbf_path}\n")

    try:
        records, fields = read_dbf(dbf_path)
        screens_map = analyze_screens(records)

        # Salvar JSON
        output_file = 'screens_map.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(screens_map, f, indent=2, ensure_ascii=False)

        print(f"✅ Mapeamento salvo em: {output_file}")

    except Exception as e:
        print(f"❌ Erro ao analisar DBF: {e}")
        import traceback
        traceback.print_exc()
