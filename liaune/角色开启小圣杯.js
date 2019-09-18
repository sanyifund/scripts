var api = 'https://www.tinygrail.com/api/';

function postData(url, data, callback) {
  var d = JSON.stringify(data);
  if (!url.startsWith('http'))
    url = api + url;
  $.ajax({
    url: url,
    type: 'POST',
    contentType: 'application/json',
    data: d,
    xhrFields: { withCredentials: true },
    success: callback
  });
}

function initICO(id) {
  var offer = 10000;
  postData(`chara/init/${id}/${offer}`, null, function (d, s) {
    if (d.State === 0) {
      console.log(id+'启动ICO成功。');
    } else {
      console.log(d.Message);
    }
  });
}

var i=0;
chara=[21595,21596]; //角色bgmid数组

function openup(){
	if(i<chara.length){
		initICO(chara[i]);
		i++;
		setTimeout("openup()",2000);
	}
}
openup();