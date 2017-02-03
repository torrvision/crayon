package = "crayon"
version = "0.4-1"
source = {
  url = "https://raw.githubusercontent.com/torrvision/crayon/90c3787e04b614473de5e4a9174f8f9686e65716/client/lua/crayon.lua"
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
