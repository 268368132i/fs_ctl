## Scripts that communicate with FreeSwitch
This portion of the project is responsible for getting data into and out of FreeSwitch.

---

**`check.py`** accesses a database and is called from FreeSwitch's Dialplan like this:
```
<action application="set" data="data=${python(check)}" inline="true"/>
```

You can use client's variables for authentication:
```
<condition field="${ext_authenticated}" expression="^true|false$">
	  <action application="answer"/>
	  <action application="conference" data="${conf_num}@video-mcu-stereo-480++flags{${conf_flags}}"/>
	  <anti-action application="log" data="ERR ext_auth condition failed"/>
</condition>
```

Here you can see that `ext_authenticated` reflects whether the user has access and `conf_flags` provide conference settings according user's permissions.
**Check database access settings** at the beginning of the script.
You might need to check FreeSwitch's documentation for executing python scripts.

---

**`comm_socket.py`** is a simple wrapper for FreeSwitch's ESL to text based Unix socket. You might want to change ip and credenticals in this file. You'll need to run this script manually.
**This script requires `ESL.so` and `ESL.py` libraries from FreeSwitch!**