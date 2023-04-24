# [3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters) :thumbsup:

![](https://img.shields.io/badge/-Medium-ffaf00.svg?style=for-the-badge)
![](https://img.shields.io/date/1681022331?label=Last%20Change&style=for-the-badge)

![](https://img.shields.io/badge/-Hash Table-3454d1.svg?style=flat-square) ![](https://img.shields.io/badge/-String-00a7e1.svg?style=flat-square) ![](https://img.shields.io/badge/-Sliding Window-efd3d7.svg?style=flat-square)

<a href="https://leetcode.com/problems/longest-substring-with-at-most-two-distinct-characters">Longest Substring with At Most Two Distinct Characters</a> | <a href="https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters">Longest Substring with At Most K Distinct Characters</a> | <a href="https://leetcode.com/problems/subarrays-with-k-different-integers">Subarrays with K Different Integers</a> | <a href="https://leetcode.com/problems/maximum-erasure-value">Maximum Erasure Value</a> | <a href="https://leetcode.com/problems/number-of-equal-count-substrings">Number of Equal Count Substrings</a> | <a href="https://leetcode.com/problems/minimum-consecutive-cards-to-pick-up">Minimum Consecutive Cards to Pick Up</a> | <a href="https://leetcode.com/problems/longest-nice-subarray">Longest Nice Subarray</a> | <a href="https://leetcode.com/problems/optimal-partition-of-string">Optimal Partition of String</a>

## Problem

Given a string ```s```, find the length of the **longest** **substring** without repeating characters.
 
**Constraints:**
	
- ```0 <= s.length <= 5 * 104```
	
- ```s``` consists of English letters, digits, symbols and spaces.

=== "Example 1"

    ```bash
    Input: s = "abcabcbb"
    Output: 3
    Explanation: The answer is "abc", with the length of 3.
    ```

=== "Example 2"

    ```bash
    Input: s = "bbbbb"
    Output: 1
    Explanation: The answer is "b", with the length of 1.
    ```

=== "Example 3"

    ```bash
    Input: s = "pwwkew"
    Output: 3
    Explanation: The answer is "wke", with the length of 3.
    Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.
    ```

**Complexity:**

* Time complexity : O(n).
* Space complexity : O(n).

## Solution