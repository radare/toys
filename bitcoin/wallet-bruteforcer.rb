#!/usr/bin/ruby -w

passphrase = "oops"

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

def scramble(passphrase)
  characters = " !\"\#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
  list = []

  # transpose adjacent chars
  (passphrase.length - 1).times do |i|
    testphrase = passphrase.dup
    testphrase[i] = passphrase[i+1]
    testphrase[i+1] = passphrase[i]
    list << testphrase
  end

  # delete one char
  passphrase.length.times do |i|
    testphrase = passphrase.dup
    testphrase = testphrase[0,i] + testphrase[(i+1)..-1]
    list << testphrase
  end

  # substitutute one char
  passphrase.length.times do |i|
    characters.chars.each do |c|
      testphrase = passphrase.dup
      testphrase[i] = c
      list << testphrase
    end
  end

  # insert one char
  (passphrase.length + 1).times do |i|
    characters.chars.each do |c|
      testphrase = passphrase.dup
      testphrase.insert(i, c)
      list << testphrase
    end
  end

  return list.uniq
end

list1 = scramble(passphrase)
list1.each { |i| test i }
list1.each { |i| scramble(i).each { |j| test j }}

puts "No luck."
exit 1
