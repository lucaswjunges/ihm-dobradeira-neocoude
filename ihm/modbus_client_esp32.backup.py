Traceback (most recent call last):
  File "/home/lucas-junges/anaconda3/bin/ampy", line 8, in <module>
    sys.exit(cli())
             ~~~^^
  File "/home/lucas-junges/.local/lib/python3.13/site-packages/click/core.py", line 1442, in __call__
    return self.main(*args, **kwargs)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/home/lucas-junges/.local/lib/python3.13/site-packages/click/core.py", line 1363, in main
    rv = self.invoke(ctx)
  File "/home/lucas-junges/.local/lib/python3.13/site-packages/click/core.py", line 1830, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
                           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "/home/lucas-junges/.local/lib/python3.13/site-packages/click/core.py", line 1226, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lucas-junges/.local/lib/python3.13/site-packages/click/core.py", line 794, in invoke
    return callback(*args, **kwargs)
  File "/home/lucas-junges/anaconda3/lib/python3.13/site-packages/ampy/cli.py", line 129, in get
    print(contents.decode("utf-8"))
          ~~~~~~~~~~~~~~~^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe3 in position 49: invalid continuation byte
