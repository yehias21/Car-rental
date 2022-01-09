function hexToBase64(hexStr) {
 let base64 = "";
 for(let i = 0; i < hexStr.length; i++) {
   base64 += !(i - 1 & 1) ? String.fromCharCode(parseInt(hexStr.substring(i - 1, i + 1), 16)) : ""
 }
 return btoa(base64);
}


function hex2img(hexstr){
    b64str = hexToBase64(hexstr);
    const base = "data:image/jpeg;base64,";
    return base + b64str
}