#!/usr/bin/ruby -w

passphrase = "oops"
characters = " !\"\#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"

def test(phrase)
  print phrase, "\t"
  system("./bitcoind", "walletpassphrase", phrase, "20")
  case $?.exitstatus
  when 0
    puts "Found it!  #{phrase}"
    exit 0
  when 127
    puts "bitcoind not found in current dir"
    exit 1
  end
end

# transpose adjacent chars
(passphrase.length - 1).times do |i|
  testphrase = passphrase.dup
  testphrase[i] = passphrase[i+1]
  testphrase[i+1] = passphrase[i]
  test testphrase
end

# delete one char
passphrase.length.times do |i|
  testphrase = passphrase.dup
  testphrase = testphrase[0,i] + testphrase[(i+1)..-1]
  test testphrase
end

# substitutute one char
passphrase.length.times do |i|
  characters.chars.each do |c|
    testphrase = passphrase.dup
    testphrase[i] = c
    test testphrase
  end
end

# insert one char
(passphrase.length + 1).times do |i|
  characters.chars.each do |c|
    testphrase = passphrase.dup
    testphrase.insert(i, c)
    test testphrase
  end
end


puts "No luck."
exit 1
