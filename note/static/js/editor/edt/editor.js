

/* 

Editor function definations

*/
// available editor options
const _actionFuncs = {
    header: (txt = 'HEADER', lvl = 1) => {
        const t = txt.replace(/#*/, '').replace(/^\s*/, '');
        return `${'#'.repeat(lvl)} ${t}`;
    },
    bold: (txt = 'BOLD') => {
        const _t = txt.match(/^\_\_(.*?)\_\_$/);
    
        if (_t && _t.length === 2) {
            return _t[1];
        };
    
        const __t = txt.match(/^\*\*(.*?)\*\*$/);
    
        if (__t && __t.length === 2) {
            return __t[1];
        };
    
        return `__${txt}__`;
    },
    italicize: (txt = 'ITALIC') => {
        const _t = txt.match(/^\_([^\*])\_$/);
    
        if (_t && _t.length === 2) {
            return _t[1];
        };
    
        const __t = txt.match(/^\*([^\*])\*$/);
    
        if (__t && __t.length === 2) {
            return __t[1];
        };
    
        return `_${txt}_`;
    },
    strike: (txt = 'STRIKE') => {
        const _t = txt.match(/^\~\~(.*?)\~\~$/);
    
        if (_t && _t.length === 2) {
            return _t[1];
        };
    
        return `~~${txt}~~`;
    },
    quote: (txt = 'BLOCKQUOTE') => {
        const _t = txt.match(/^\>(.*?)\n\n$/sm);
    
        if (_t && _t.length === 2) {
            return _t[1].replace(/^\s*/, '');
        };
    
        return `> ${txt}\n\n`;
    },
    code: (txt = 'CODE', ml = true) => {
        let res = '';
        if (ml) {
            const _t = txt.match(/\`\`\`\n(.*?)\n\`\`\`/sm);
    
            if (_t && _t.length === 2) {
                return _t[1];
            };
    
            res = `\`\`\`\n${txt}\n\`\`\``;
    
        } else {
            const __t = txt.match(/^\`(.*?)\`$/);
    
            if (__t && __t.length === 2) {
                return __t[1];
            };
    
            res = `\`${txt.replace(/\n/g, '')}\``;
        };
    
        return res;
    },
    list: (txt = '', ord = false) => {
        const itemMark = ord? '1. ': '* ';
        const markRegEx = ord? /1\.\s/: /\*\s/;
    
        const mI = (t = '', m = itemMark) => {
            if (t.search(markRegEx) > -1) {
                return t.replace(markRegEx, '');
            } else {
                const _pos = t.search(/[^\s]/);
                return _pos > -1? `${t.substring(0, _pos)}${m}${t.substring(_pos)}`: `${m}${t}`;
            }
        };
    
        const _t = txt.match(/^(.*?)$/gsm);
    
        if (_t && _t.length > 1) {
            return _t.map((__t) => mI(__t)).join('\n');
        };
    
        return mI(txt);
    },
    case: (txt = '', cs = 0) => {
        /* 
        upper     -  0
        lower     -  1
        title     -  2
        sentence  -  3
        */
        let text;

        const capitalize = (t = '') => t === ''? '':`${t[0].toUpperCase()}${t.substring(1).toLowerCase()}`;

        switch (cs) {
            case 0:
                text = txt.toUpperCase();
                break;
            
            case 1:
                text = txt.toLowerCase();
                break;
            
            case 2:
                text = txt.split(' ').map((w) => capitalize(w)).join(' ');
                break;

            case 3:
                text = txt.split('. ').map((w) => capitalize(w)).join('. ');
                break;

            default:
                text = txt;
                break;
        };

        return text;
    }
};


const _actions = new Map ([
    ['bold', _actionFuncs.bold],
    ['italic', _actionFuncs.italicize],
    ['strike', _actionFuncs.strike],
    ['quote', _actionFuncs.quote],
    ['code', _actionFuncs.code],
    ['s-code', ((txt = '') => _actionFuncs.code(txt, false))],
    ['bullets', ((txt = '') => _actionFuncs.list(txt))],
    ['numbers', ((txt = '') => _actionFuncs.list(txt, true))],
    ['case-u', ((txt = '') => _actionFuncs.case(txt, 0))],
    ['case-l', ((txt = '') => _actionFuncs.case(txt, 1))],
    ['case-t', ((txt = '') => _actionFuncs.case(txt, 2))],
    ['case-s', ((txt = '') => _actionFuncs.case(txt, 3))],
    ['link', '[Text](link title)'],
    ['image', '![altText](src title)'],
    ['line', '- - -\n']
].concat(Array.from(Array(6), (_, i) => ++i).map((h) => {
    return [`h${h}`, ((txt = '') => _actionFuncs.header(txt, h))];
})));
// last line adds h1 - h6 progmatically




/* 
    Editor caret selecetion and text input
*/
const edt = document.getElementById('note-edit');


// get the position of the cursor on the textarea
const getCursorPos = (editor = edt) => ({start: editor.selectionStart, end: editor.selectionEnd});


// get selected text
const getTextAtPos = (pos = getCursorPos(), txt = edt.value) => txt.substring(pos.start, pos.end);

// insert text to editor
function insertText (newText = '', focus = true, wh = edt, pos = getCursorPos()) {
    const og = wh.value;
    wh.value = og.substring(0, pos.start) + newText + og.substring(pos.end);
    wh.selectionStart = focus? pos.start: pos.start + newText.length;
    wh.selectionEnd = pos.start + newText.length
    edt.focus();
};


/* 
    Listen for actions
*/

[...document.getElementsByClassName('shortcut-item')].forEach((shortcut) => {
    const short = shortcut.dataset.short;

    if (_actions.has(short)) {
        if (['link', 'image', 'line'].includes(short)) {
            shortcut.addEventListener('click', () => insertText(_actions.get(short)));
        } else {
            shortcut.addEventListener('click', (e) => {
                const nt = getTextAtPos();
                const ntt = _actions.get(short)(nt);
                insertText(ntt);
            });
        }

    };

});

// let tab key add 4 spaces
edt.addEventListener('keydown', (event) => {
    if (event.key === 'Tab') {
        event.preventDefault();
        insertText('    ', false);
    };

    if (event.ctrlKey) {
        switch (event.key) {
            // bold
            case 'b':
                event.preventDefault();
                if (getTextAtPos() !== '') {
                    insertText(_actions.get('bold')(getTextAtPos()));
                };
                break;

            // italicize
            case 'i':
                event.preventDefault();
                if (getTextAtPos() !== '') {
                    insertText(_actions.get('italic')(getTextAtPos()));
                };
                break;

            // strike through
            case 'q':
                event.preventDefault();
                if (getTextAtPos() !== '') {
                    insertText(_actions.get('strike')(getTextAtPos()));
                };
                break;

            // insert link
            case '.':
                event.preventDefault();
                if (getTextAtPos() === '') {
                    insertText(_actions.get('link'), false)
                };
                break;

            // add insert image
            case '/':
                event.preventDefault();
                if (getTextAtPos() === '') {
                    insertText(_actions.get('image'), false);
                };
                break;
        
            default:
                break;
        }
    };
});


/* 
    font size control
*/
const sizeX = document.getElementById('f-size');

if (sizeX) {
    const changeFontSize = (newValue, wh = edt, h = sizeX) => {
        const nv = +newValue;

        if (nv !== NaN && ((6 < nv) && (nv < 20))) {
            wh.style.fontSize = `${nv}px`;
            h.value = nv;
        };
    };

    sizeX.addEventListener('change', (event) => {
        event.preventDefault();
        changeFontSize(event.target.value);
    })

    sizeX.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            changeFontSize(event.target.value);
        }
    });

};
