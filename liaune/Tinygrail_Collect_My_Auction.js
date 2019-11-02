var api = 'https://tinygrail.com/api/';
function getData(url, callback) {
  if (!url.startsWith('http'))
    url = api + url;
  $.ajax({
    url: url,
    type: 'GET',
    xhrFields: { withCredentials: true },
    success: callback
  });
}
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
var username = $('#dock .clearit li.first a')[0].innerText;
getData(`chara/user/auction/1/1000`,function (d, s) {
	var chara = {};
	document.write('<table><tbody><tr><th>User</th><th>ID</th><th>角色</th><th>出价</th><th>数量</th></tr></tbody><tbody>');
	for(i=0;i<d.Value.Items.length; i++){
		var Id = d.Value.Items[i].CharacterId;
		var State = d.Value.Items[i].State;
		chara[Id] = {};
		chara[Id].Id = d.Value.Items[i].CharacterId;
		chara[Id].Name = d.Value.Items[i].Name;
		chara[Id].Price = d.Value.Items[i].Price;
		chara[Id].Amount = d.Value.Items[i].Amount;
		if(chara[Id].Price && chara[Id].Amount && State==0)
		document.write('<tr><td>'+username+'<td><a href="https://bgm.tv/character/'+Id+'" class="l">'+Id+'</a></td><td>'+chara[Id].Name+'</td><td>'+chara[Id].Price+'</td><td>'+chara[Id].Amount+'</td></tr>');
	}
	//console.table(chara);
});
