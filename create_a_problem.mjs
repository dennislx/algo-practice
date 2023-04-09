import fs from 'fs';
import fse from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import cheerio from 'cheerio';
import axios from 'axios';
import colors from './config/colors.json' assert {type: "json"};
import problems from './config/problems.json' assert {type: "json"};


var currentDir = new URL('.', import.meta.url).pathname;

const create = data => {

    const dir = getPath(data.questionId, data.questionTitle);

    // if (fs.existsSync(dir)) {
    //     console.log(`${chalk.red('file already exists')}: ${chalk.blue(dir)}\n`);
    //     return;
    // }
    let str = fs.readFileSync(`${currentDir}/template.md`, 'utf-8');

    const pageData = getPageData(data);
    Object.keys(pageData).forEach(name => {
        str = str.replace(`{{${name}}}`, pageData[name]);
    });

    fse.outputFileSync(dir, str);

    console.log(`created at: ${chalk.blue(dir)}\n`);
};

const getPageData = (data) => {
    const {
        questionTitleSlug: slug, questionId: id, questionTitle: name,
        likes, dislikes, topicTags: topics, similarQuestions: similar,
        difficulty: diff
    } = data;
    const pageData = {
        id: id,
        name: name,
        difficulty: getDifficulty(diff),
        createtime: Math.floor(Date.now() / 1000),
        link: `https://leetcode.com/problems/${slug}`,
        relatedTopics: topics.map(t => {
            const a = t.name.replaceAll('-', '--'), b = colors[t.name];
            return `![](https://img.shields.io/badge/-${a}-${b}.svg?style=flat-square)`
        }).join(' '),
        similarQuestions: JSON.parse(similar).map(q => {
            return `<a href="https://leetcode.com/problems/${q.titleSlug}">${q.title}</a>`;
        }).join(' | '),
        emoji: likes > dislikes ? ':thumbsup:' : ':thumbsdown:',
        ...getDescription(data.content)
    }
    return pageData;
}

const getDifficulty = (diff) => {
    const color = diff === 'Easy' ? "00a690" : diff === 'Medium' ? "ffaf00" : "ff284b";
    return `![](https://img.shields.io/badge/-${diff}-${color}.svg?style=for-the-badge)`
}

const getDescription = (description) => {
    const rules = [
        {
            regexp: /<pre>([\s\S]*?)<\/pre>/ig,
            replacer: (_, $1) => `\`\`\`\n${cheerio.load($1).text().replace(/\n$/, '')}\n\`\`\``
        },
        {
            regexp: /<code>(.*?)<\/code>/ig,
            replacer: (_, $1) => `\`\`\`${$1}\`\`\``
        },
        {
            regexp: /<i>(.*?)<\/i>/ig,
            replacer: (_, $1) => `*${$1}*`
        },
        {
            regexp: /<b>(.*?)<\/b>/ig,
            replacer: (_, $1) => `**${$1}**`
        },
        {
            regexp: /<em>(.*?)<\/em>/ig,
            replacer: (_, $1) => `**${$1}**`
        },
        {
            regexp: /<img.*src="([^"]+)".*\/?>/ig,
            replacer: (_, $1) => `\n![](${$1})\n`
        },
        {
            regexp: /<strong>(.*?)<\/strong>/ig,
            replacer: (_, $1) => `**${$1}**`
        },
        {
            regexp: /<\/?ul>/ig,
            replacer: '',
        },
        {
            regexp: /<li>(.*?)<\/li>/ig,
            replacer: (_, $1) => `\n- ${$1}`
        }
    ];
    let html = description;
    rules.forEach(rule => {
        html = html.replace(rule.regexp, rule.replacer);
    });
    const text = cheerio.load(html).text();
    return splitContent(text);
};

const template = `
=== "{{example}}"

    {{code}}
`

const splitContent = (text) => {
    /**
     * @exampleRegex        match example header and its following conotent (gi: global case insensitive)
     *                      [\s\S]*? part matches any character,  (?=\n{2}|$) specifies ending pattern
     * @endingRegex         match example with **xxx** in the end
     */
    const exampleRegex = /(Example \d+: *\n+[\s\S]*?)(?=\n{2,3}|$)/gi;
    const endingRegex = /\*\*[\s\S]+\*\*/i;
    let [heading, ...examples] = text.split(exampleRegex);
    const lastText = examples.pop();
    const match = endingRegex.exec(lastText);
    examples.push(lastText.substring(0, match.index).trim());
    heading += lastText.substring(match.index).replaceAll('\n\n', '\n').trim()
    return {
        heading: heading.replaceAll('\n\n', '\n'),
        example: examples
            .filter(x => x.trim().startsWith('Example'))
            .map(x => {
                const [title, code] = x.split('\n\n');
                let res = `=== "${title.replace(/:$/, '')}"\n\n`;
                res += code.split('\n').map(
                    (line, idx) => `    ${line}${idx === 0 ? 'bash' : ''}`
                ).join('\n');
                return res;
            })
            .join('\n\n')
    }
}

const getPath = (id, name) => {
    /**
     * file:///home/dalab1/project/web-dev/blog/dennisl/my_leetcode/001-100/1.%20Two%20Sum.md
     */
    const _id = id.padStart(4, '0');
    const _path = `${currentDir}/../main/solutions/${_id}. ${name}/readme.md`;
    return _path;
};

const getName = id => {
    const url = `https://leetcode.com/problems/${problems[id.padStart(4, '0')]}`;
    const res = /https:\/\/leetcode.com\/problems\/([^/]+)/.exec(url);
    if (!res) throw new Error('leetcode problem url not valid');
    return res[1];
}

const getDate = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1; // add 1 since getMonth() returns a zero-based index
    const date = now.getDate();
    return `${year}/${month}/${date}`;
}

const name = getName(process.argv[2]);

let queryStr = `query getQuestionDetail($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        questionId
        questionTitle
        questionTitleSlug
        content
        difficulty
        likes
        dislikes
        stats
        similarQuestions
        categoryTitle
        topicTags { name }
      }
    }
    &operationName=getQuestionDetail&variables={"titleSlug":"${name}"}`
const url = 'https://leetcode.com/graphql?query=' + encodeURIComponent(queryStr)
    .replaceAll('%24', '$')
    .replaceAll('%26', '&')
    .replaceAll('%3D', '=');
axios.get(url).then(res => {
    create(res.data.data.question);
}).catch(err => {
    console.error(err);
});