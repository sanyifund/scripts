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

function appendICO(id,feed) {
  var url = api + `chara/`+id;
  var offer = feed;
  $.get(url, function (d, s) {
	var ico_id = d.Value.Id;
	console.log(d);
	postData(`chara/join/${ico_id}/${offer}`, null, function (d, s) {
    if (d.State === 0) {
      console.log(id+'追加注资成功。');
    } else {
      alert(d.Message);
    }
  });
  });
  
}
function pushup(){
	if(i<chara.length){
		var feed = feeds[i]? feeds[i]:1000;
		appendICO(chara[i],feed);
		i++;
		setTimeout("pushup()",1000);
	}
}
var i=0;
chara =[]; //角色bgmId数组
feeds = []; //每个角色的注资金额，若为空默认1000
pushup();
