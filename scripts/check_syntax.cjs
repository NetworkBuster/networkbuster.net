const fs = require('fs');
const path = require('path');
const s = fs.readFileSync(path.join(__dirname, '..', 'server.js'), 'utf8');
function count(char){return (s.split(char).length-1);} 
console.log('backticks', count('`'));
console.log('single quotes', count("'"));
console.log('double quotes', count('"'));
console.log('open paren', count('('), 'close paren', count(')'));
console.log('open brace', count('{'), 'close brace', count('}'));
console.log('open bracket', count('['), 'close bracket', count(']'));
console.log('length', s.length);

// find line where braces go out of balance
let openP = 0, openB = 0, openC = 0;
const lines = s.split(/\r?\n/);
for (let i=0;i<lines.length;i++){
  const line = lines[i];
  for (const ch of line){ if (ch==='(') openP++; if (ch===')') openP--; if (ch==='{') openB++; if (ch==='}') openB--; if (ch==='[') openC++; if (ch===']') openC--; }
  if (openP<0){ console.log('unbalanced paren at line', i+1); break; }
  if (openB<0){ console.log('unbalanced brace at line', i+1); break; }
  if (openC<0){ console.log('unbalanced bracket at line', i+1); break; }
}
if (openP>0) console.log('missing ) by', openP);
if (openB>0) console.log('missing } by', openB);
if (openC>0) console.log('missing ] by', openC);

