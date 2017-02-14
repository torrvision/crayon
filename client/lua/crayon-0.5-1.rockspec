package = "crayon"
version = "0.5-1"
source = {
   url = "https://raw.githubusercontent.com/torrvision/crayon/7f2f96b6a44b6729cc0f5feae5d09df70b6eba19/client/lua/crayon.lua"
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
