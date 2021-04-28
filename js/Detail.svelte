<svelte:window on:keydown={keydown} />

<script>
import Vote from './Vote.svelte'
export let meme;
export let selected;
export let username;

function keydown(evt) {
	if(evt.key == 'Escape') {
		selected = null;
	}
}

function clickCancel(evt) {
	if(evt.target.classList.contains('meme')) {
		selected = null;
	}
}

</script>

<style>
div.meme {
	position: fixed;
	background: rgba(255, 255, 255, 0.9);
	width: 100vw;
	height: 100vh;
	z-index: 100;
	top: 0px;
	left: 0px;
	display: flex;
	justify-content: center;
}
.img-container {
	text-align: center;
}
img {
	height: 80vh;
}
</style>

<div class="meme" on:click={clickCancel}>
	<div>
		<h1># { meme.rank }</h1>
		<img src={meme.path}>
		<Vote {meme} {username} />
	</div>
</div>
