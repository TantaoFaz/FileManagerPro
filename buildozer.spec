[app]
title = DuckBusca
package.name = duckbusca
package.domain = com.hub
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,requests
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
orientation = portrait
fullscreen = 0
android.allow_backup = True

[buildozer]
log_level = 2
