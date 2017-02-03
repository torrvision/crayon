package = "crayon"
version = "0.4-1"
source = {
  url = "https://github.com/torrvision/crayon/tree/master/client/lua",
  tag = "v0.4"
}

description = {
  summary = "A lua client for crayon.",
  homepage = "https://github.com/torrvision/crayon"
}

dependencies = {
  "lua-requests",
}

build = {
  type = "builtin",
  modules = {
    crayon = "crayon.lua"
  }
}
