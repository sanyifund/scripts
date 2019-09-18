var api = 'https://www.tinygrail.com/api/';
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
function getUsers(chara){
	var Id = chara.Id;
	var Name = chara.Name;
	var Bonus = chara.Bonus;
	getData(`chara/users/${Id}/1/10`,function (d, s) {
		var TotalItems = d.Value.TotalItems;
		var chairmanId = d.Value.Items[0].name;
		var chairman = d.Value.Items[0].Nickname;
		var Balance = d.Value.Items[0].Balance;
		document.write('<tr><td><a href="https://bgm.tv/character/'+Id+'" class="l">'+Id+'</a></td><td>'+Name+'</td><td>'+Bonus+'</td><td>'+TotalItems+'</td><td><a href="https://bgm.tv/user/'+chairmanId+'" class="l">'+chairman+'</a></td><td>'+Balance+'</td><tr>');
	});
}
getData(`chara/mrc/1/1000`,function (d, s) {
	var chara = [];
	for(i=0;i<d.Value.length; i++){
		state = {};
		state.Id = d.Value[i].Id;
		state.Name = d.Value[i].Name;
		state.Bonus = d.Value[i].Bonus;
		chara.push(state);
	}
	document.write('<table><tbody><tr><th>ID</th><th>角色</th><th>新番期数</th><th>股东数</th><th>主席</th><th>股数</th></tr></tbody><tbody>');
	i = 0;
    let getitemsList= setInterval(function(){
		getUsers(chara[i]);
		i++;
        if(i >= chara.length){
            clearInterval(getitemsList);
        }
    },100);
});
