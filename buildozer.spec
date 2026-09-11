[app]

title = Attendance
package.name = attendance
package.domain = org.damir

source.dir = .
source.include_exts = py,json,png,jpg,kv

version = 1.0

requirements = python3,kivy

orientation = portrait

fullscreen = 0


[buildozer]

log_level = 2
warn_on_root = 1


[android]

android.api = 35
android.minapi = 21

android.archs = arm64-v8a

android.allow_backup = True

android.permissions =

