/**
 * still incorrect with large numbers...
 */
var countAnagrams = function (s) {
    function factorial(n) {
        if (n === 0 || n === 1)
            return 1;
        else
            return n * factorial(n - 1);
    }
    // count of each word, too => {t: 1, o: 2}
    function helper(word) {
        const count = {};
        const n = word.length;
        for (let i = 0; i < n; i++) {
            (c = word[i]);
            count[c] = (count[c] || 0) + 1
        }
        const denomenator = Object.values(count).reduce((prod, x) => prod * factorial(x), 1);
        const numerator = factorial(n);
        return BigInt(numerator) / BigInt(denomenator);
    }
    let n = BigInt(1);
    const MODULO = BigInt(1000000007);
    s.split(" ").forEach(w => {
        console.log(helper(w));
        n *= helper(w);
    })
    return n % MODULO;
};