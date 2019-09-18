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
function getICO(id) {
	getData(`chara/initial/users/${id}/1`,function (d, s) {
		var data = d.Value.Items[0];
		var name = data.Name;
		getData(`chara/user/assets/${name}/true`, function (d, s) {
			var data = d.Value;
			for (i = 0; i < data.Initials.length; i++) {
				var CharacterId = data.Initials[i].CharacterId;
				var ico_id = data.Initials[i].Id;
				if(ico_id == id){
					getData(`chara/${CharacterId}`, function (d, s) {
						var Id = d.Value.Id;
						var CharacterId = d.Value.CharacterId;
						var Name = d.Value.Name;
						var Link = 'https://bgm.tv/character/'+ CharacterId;
						var Bonus = d.Value.Bonus;
						var Total = d.Value.Total;
						var Users = d.Value.Users;
						var Begin = d.Value.Begin;
						var End = d.Value.End;
						var SubjectName = d.Value.SubjectName;
						var SubjectLink = 'https://bgm.tv/subjetct'+ d.Value.SubjectId;
						document.write('<tr><td>'+Id +'</td><td><a href="'+Link+'" class="l">'+CharacterId+'</a></td><td>'+Name+'</td><td>'+Bonus+'</td><td>'+Total+'</td><td>'+Users+'</td><td>'+End+'</td></tr>');
					});
				}
			}
		}); 
	}); 
}
function pushup(){
	if(end > start){
		getICO(start);
		start++;
		setTimeout("pushup()",2000);
	}
}
var start=2010;
var end = 2030;
document.write('<table><tbody><tr><th>ICO_Id</th><th>角色Id</th><th>角色名</th><th>新番期数</th><th>筹集金额</th><th>人数</th><th>ICO结束时间</th></tr></tbody><tbody>');
pushup();
