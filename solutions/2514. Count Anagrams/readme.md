# [2605. Count Anagrams](https://leetcode.com/problems/count-anagrams) :thumbsup:

![](https://img.shields.io/badge/-Hard-ff284b.svg?style=for-the-badge)
![](https://img.shields.io/date/1682363574?label=Last%20Change&style=for-the-badge)

![](https://img.shields.io/badge/-Hash Table-3454d1.svg?style=flat-square) ![](https://img.shields.io/badge/-Math-d1345b.svg?style=flat-square) ![](https://img.shields.io/badge/-String-00a7e1.svg?style=flat-square) ![](https://img.shields.io/badge/-Combinatorics-4a5759.svg?style=flat-square) ![](https://img.shields.io/badge/-Counting-577590.svg?style=flat-square)

<a href="https://leetcode.com/problems/group-anagrams">Group Anagrams</a> | <a href="https://leetcode.com/problems/count-ways-to-build-rooms-in-an-ant-colony">Count Ways to Build Rooms in an Ant Colony</a>

## Problem

You are given a string ```s``` containing one or more words. Every consecutive pair of words is separated by a single space ```' '```.
A string ```t``` is an **anagram** of string ```s``` if the ```ith``` word of ```t``` is a **permutation** of the ```ith``` word of ```s```.

	
- For example, ```"acb dfe"``` is an anagram of ```"abc def"```, but ```"def cab"``` and ```"adc bef"``` are not.

Return **the number of **distinct anagrams** of **```s```. Since the answer may be very large, return it **modulo** ```109 + 7```.
 
**Constraints:**
	
- ```1 <= s.length <= 105```
	
- ```s``` consists of lowercase English letters and spaces ```' '```.
	
- There is single space between consecutive words.

=== "Example 1"

    ```bash
    Input: s = "too hot"
    Output: 18
    Explanation: Some of the anagrams of the given string are "too hot", "oot hot", "oto toh", "too toh", and "too oht".
    ```

=== "Example 2"

    ```bash
    Input: s = "aa"
    Output: 1
    Explanation: There is only one anagram possible for the given string.
    ```

**Complexity:**

* Time complexity : O(n).
* Space complexity : O(n).

## Solution