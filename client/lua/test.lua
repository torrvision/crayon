local crayon = require("crayon")


-- A clean server should be running on the test_port with:
-- docker run -it -p 7998:8888 -p 7999:8889 --name crayon_lua_test alband/crayon
local test_port = 7999

local cc = crayon.CrayonClient("localhost", test_port)

-- Check empty
local xp_list = cc:get_experiment_names()
for k,v in pairs(xp_list) do
  error("The server should be empty")
end

-- Check create / add scalar
local foo = cc:create_experiment("foo")
foo:add_scalar_value("bar", 3)
foo:add_scalar_value("bar", 4, 123)
xp_list = cc:get_experiment_names()
for k,v in pairs(xp_list) do
  if v ~= "foo" then
    error("The server should not contain xp: "..v)
  end
end
local bar_values = foo:get_scalar_values("bar")
for i,v in ipairs(bar_values) do
  if i==2 and v[1] ~= 123 then
    error("wall_time was not set properly")
  end
  if v[2] ~= i-1 then
    error("step was not incremented properly")
  end
  if v[3] ~= i+2 then
    error("value was not set properly")
  end
end

-- Check open
local foo_bis = cc:open_experiment("foo")
for k,v in pairs(xp_list) do
  if v ~= "foo" then
    error("The server should not contain xp: "..v)
  end
end
local bar_values = foo_bis:get_scalar_values("bar")
for i,v in ipairs(bar_values) do
  if i==2 and v[1] ~= 123 then
    error("wall_time was not set properly")
  end
  if v[2] ~= i-1 then
    error("step was not incremented properly")
  end
  if v[3] ~= i+2 then
    error("value was not set properly")
  end
end

-- Check get backup
local zip_file = "back.zip"
foo:to_zip(zip_file)

-- Check upload backup
local foo2 = cc:create_experiment("foo2", zip_file)
for k,v in pairs(xp_list) do
  if v ~= "foo" and v~= "foo2" then
    error("The server should not contain xp: "..v)
  end
end
local bar_values = foo2:get_scalar_values("bar")
for i,v in ipairs(bar_values) do
  if i==2 and v[1] ~= 123 then
    error("wall_time was not set properly")
  end
  if v[2] ~= i-1 then
    error("step was not incremented properly")
  end
  if v[3] ~= i+2 then
    error("value was not set properly")
  end
end

os.remove(zip_file)

print("Success !")
