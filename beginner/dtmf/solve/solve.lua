local dtmf = {
	["1"] = { low = 697, high = 1209, comb = 1906 },
	["2"] = { low = 697, high = 1336, comb = 2033 },
	["3"] = { low = 697, high = 1477, comb = 2174 },
	["A"] = { low = 697, high = 1633, comb = 2330 },
	["4"] = { low = 770, high = 1209, comb = 1979 },
	["5"] = { low = 770, high = 1336, comb = 2106 },
	["6"] = { low = 770, high = 1477, comb = 2247 },
	["B"] = { low = 770, high = 1633, comb = 2403 },
	["7"] = { low = 852, high = 1209, comb = 2061 },
	["8"] = { low = 852, high = 1336, comb = 2188 },
	["9"] = { low = 852, high = 1477, comb = 2329 },
	["C"] = { low = 852, high = 1633, comb = 2485 },
	["*"] = { low = 941, high = 1209, comb = 2150 },
	["0"] = { low = 941, high = 1336, comb = 2277 },
	["#"] = { low = 941, high = 1477, comb = 2418 },
	["D"] = { low = 941, high = 1633, comb = 2574 },
}

local multitap = {
	["0"] = { " ", "0" },
	["1"] = { ".", ",", "?", "!", "1", "-", "@", "_", "+", "#" },
	["2"] = { "a", "b", "c", "2", "A", "B", "C" },
	["3"] = { "d", "e", "f", "3", "D", "E", "F" },
	["4"] = { "g", "h", "i", "4", "G", "H", "I" },
	["5"] = { "j", "k", "l", "5", "J", "K", "L" },
	["6"] = { "m", "n", "o", "6", "M", "N", "O" },
	["7"] = { "p", "q", "r", "s", "7", "P", "Q", "R", "S" },
	["8"] = { "t", "u", "v", "8", "T", "U", "V" },
	["9"] = { "w", "x", "y", "z", "9", "W", "X", "Y", "Z" },
}

local ans = {}

for k, v in pairs(dtmf) do
	ans[tostring(v.comb)] = k
end

local file = io.open("../publish/dtmf.txt", "r")
if file == nil then
	print("Missing ctf challenge file")
	os.exit(1)
end

local line = file:read()
file:close()

local decode = ""

for i = 1, #line, 4 do
	local num = line:sub(i, i + 3)
	local digit = ans[num]
	if digit then
		decode = decode .. digit
	else
		decode = decode .. "????"
	end
end

print("decoded:", decode)

local final_message = ""
local i = 1

while i <= #decode do
	local current_digit = decode:sub(i, i)
	local count = 1
	while i + 1 <= #decode and decode:sub(i + 1, i + 1) == current_digit do
		count = count + 1
		i = i + 1
	end
	if multitap[current_digit] then
		local char_index = (count - 1) % #multitap[current_digit] + 1
		final_message = final_message .. multitap[current_digit][char_index]
	end
	i = i + 1
end

local correct = "onlyninetieskidswillrememberthis"
if final_message == correct then
	print("valid decode")
else
	print("invalid decode")
end

print("Final decoded message: " .. final_message)
