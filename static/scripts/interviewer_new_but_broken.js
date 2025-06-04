 * Detected change in '/Users/jdweekley/Documents/SkillScopePrototype2/server.py', reloading
 * Restarting with stat
Traceback (most recent call last):
  File "/Users/jdweekley/Documents/SkillScopePrototype2/server.py", line 186, in <module>
    @app.route("/transcripts", methods=["GET"])
     ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jdweekley/Documents/SkillScope/venv/lib/python3.13/site-packages/flask/sansio/scaffold.py", line 362, in decorator
    self.add_url_rule(rule, endpoint, f, **options)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jdweekley/Documents/SkillScope/venv/lib/python3.13/site-packages/flask/sansio/scaffold.py", line 47, in wrapper_func
    return f(self, *args, **kwargs)
  File "/Users/jdweekley/Documents/SkillScope/venv/lib/python3.13/site-packages/flask/sansio/app.py", line 657, in add_url_rule
    raise AssertionError(
    ...<2 lines>...
    )
AssertionError: View function mapping is overwriting an existing endpoint function: list_transcripts
(venv) ITS-JWEEKLEY-01:SkillScopePrototype2 jdweekley$ python server.py
Traceback (most recent call last):
  File "/Users/jdweekley/Documents/SkillScopePrototype2/server.py", line 186, in <module>
    @app.route("/transcripts", methods=["GET"])
     ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jdweekley/Documents/SkillScope/venv/lib/python3.13/site-packages/flask/sansio/scaffold.py", line 362, in decorator
    self.add_url_rule(rule, endpoint, f, **options)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jdweekley/Documents/SkillScope/venv/lib/python3.13/site-packages/flask/sansio/scaffold.py", line 47, in wrapper_func
    return f(self, *args, **kwargs)
  File "/Users/jdweekley/Documents/SkillScope/venv/lib/python3.13/site-packages/flask/sansio/app.py", line 657, in add_url_rule
    raise AssertionError(
    ...<2 lines>...
    )
AssertionError: View function mapping is overwriting an existing endpoint function: list_transcripts