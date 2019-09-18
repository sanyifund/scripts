list = document.querySelectorAll('#grail .clearit .init_list li');
chara = [];
my_ico = 0;
list.forEach( (elem, index) => {
id = elem.querySelector('a.avatar').href.split('/character/')[1];
chara.push(id);
feed = elem.querySelector('.feed').innerText.split('/')[0].replace(/,/g, "").replace(/₵/g, "");
my_ico += parseInt(feed);
});
console.log(chara);
alert("Total ICO: "+my_ico);
