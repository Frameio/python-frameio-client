// print function
function print(msg) {
  console.log(msg);
}

// replace all
String.prototype.replaceAll = function (search, replacement) {
  return this.replace(new RegExp(search, 'g'), replacement);
};

// check vue for browser compatibility
var compatibleBrowser = typeof Object['__defineSetter__'] === 'function';
if (!compatibleBrowser) {
  alert('Sorry, but your browser has no Vue compatibility!');
}

// get hash code from str
function hashCode(str) { // java String#hashCode
  var hash = 0;
  for (var i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 8) - hash);
  }
  return hash;
}

// int (hash) to rgb
function intToRGB(i) {
  let r = (i & 0x00FF0000) >> 2 ** 4;
  let g = (i & 0x0000FF00) >> 2 ** 3;
  let b = (i & 0x000000FF);
  const limit = 100;
  r = r < limit ? limit : r;
  g = g < limit ? limit : g;
  b = b < limit ? limit : b;

  return 'rgb(' + r + ',' + g + ',' + b + ')';
}

// set caret position inside of input
function setCaretPosition(elemId, caretPos) {
  let elem = document.getElementById(elemId);

  if (elem != null) {
    if (elem.createTextRange) {
      var range = elem.createTextRange();
      range.move('character', caretPos);
      range.select();
    } else {
      if (elem.selectionStart) {
        elem.focus();
        elem.setSelectionRange(caretPos, caretPos);
      } else
        elem.focus();
    }
  }
}

function getCaretPosition(elemId) {
  let elem = document.getElementById(elemId);
  return elem.selectionStart;
}
