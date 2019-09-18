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
function getDepth(chara){
	var Id = chara.Id;
	var Name = chara.Name;
	var Bonus = chara.Bonus;
	getData(`chara/depth/${Id}`,function (d, s) {
		var AskPrice = d.Value.Asks[0] ? d.Value.Asks[0].Price : null;
		var AskAmount = d.Value.Asks[0] ? d.Value.Asks[0].Amount : 0;
		var BidPrice = d.Value.Bids[0] ? d.Value.Bids[0].Price : 0;
		var BidAmount = d.Value.Bids[0] ? d.Value.Bids[0].Amount : 0;
		document.write('<tr><td><a href="https://bgm.tv/character/'+Id+'" class="l">'+Id+'</a></td><td>'+Name+'</td><td>'+Bonus+'</td><td>'+AskPrice+'</td><td>'+AskAmount+'</td><td>'+BidPrice+'</td><td>'+BidAmount+'</td><tr>');
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
	document.write('<table><tbody><tr><th>ID</th><th>角色</th><th>新番期数</th><th>最低卖价</th><th>数量</th><th>最高买价</th><th>数量</th></tr></tbody><tbody>');
	i = 0;
    let getitemsList= setInterval(function(){
		getDepth(chara[i]);
		i++;
        if(i >= chara.length){
            clearInterval(getitemsList);
        }
    },50);
});