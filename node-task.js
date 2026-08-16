function minimalOperations(words) {
  return words.map((word) => {
    let count = 0;
    for (let i = 0; i < word.length + 1; i++) {
      if (word[i - 1] === word[i]) {
        count += 1;
        i += 1;
      }
    }
    return count;
  });
}

function minimalOperationsRegex(words) {
  return words.map((word) => word.match(/(.)\1/g)?.length ?? 0);
}

testMock = [
  "abaaaaaaaababab",
  "zqzcdhefjzuqfkigwydqalimitpkwduxsauxslqanstag",
  "vmggdujscxesizsjycskimjtqfcoctyrgxjdpyeowavlriojizsrggnywkijdodicyhfreurltzaouzksugugn",
  "ouojrgpgkuixdbuddltrvfpjzzwafmqdmmku",
  "zqbfnhbabvfavoztvohurpgicqtczwnxvlxxtvuglaqltafawjcwgagjinrdmobhnauebvgdufxegtbgaqysfwdqyhsgloahwnb",
  "lasoembsbtjgwacvuvygavlwfuedjwwhyhyjwxkfbtofjogogkjojyxncfmekmowcjmk",
  "rdfrxmmwwgyfwrboqfnwpngroegtkfoyypektjj",
  "gpslaqjtcxixtsucjvjolxjbndilpdtzxdndlow",
  "xwrhmpcsqmednmqzthrtjlnggvfpmdqkfadhe",
];

const res = minimalOperations(testMock);

const res2 = minimalOperationsRegex(testMock);
console.log(res);
console.log(res2);
