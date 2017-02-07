package = "crayon"
version = "0.5-1"
source = {
   url = "https://raw.githubusercontent.com/torrvision/crayon/0dcaed65d306aa5005a1f4c05d41949b78c341e1/client/lua/crayon.lua",
   md5 = "d0c73b17d2b23696bd036b8e3f3d62b3"
}
description = {
   summary = "A lua client for crayon.",
   homepage = "https://github.com/torrvision/crayon"
}
dependencies = {
   "lua-requests"
}
build = {
   type = "builtin",
   modules = {
      crayon = "crayon.lua"
   }
}
