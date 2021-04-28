<script>
export let meme;
export let username;

async function vote(meme) {
	const req = await fetch(meme.path, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer ' + localStorage.getItem('memetoken'),
		},
		body: JSON.stringify({like: meme.liked.indexOf(username) < 0}),
	});
}
</script>

<style>
button img {
	width: 20px;
	margin-right: 5px;
}
button {
	border: 0;
	background: transparent;
	cursor: pointer;
	display: inline-flex;
	align-items: center;
	margin-top: 3px;
	outline: none;
}
button img {
	opacity: 0.5;
}
button.liked img {
	opacity: 1;
}
</style>


<div style="display: flex; justify-content: space-between; align-items: center;">
	<button on:click={() => vote(meme)} class:liked={meme.liked.indexOf(username) >= 0}>
		<img src="https://cdn.frankerfacez.com/emoticon/381875/4" width="20px">
		{meme.liked.length}
	</button>
	<span style="text-align: right">
		{(new Date(meme.updated)).toLocaleString('cs')}
	</span>
</div>
