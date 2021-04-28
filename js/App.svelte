<svelte:window on:mousemove={mousemove} />

<script>
import { flip} from 'svelte/animate'
import { crossfade, fade } from 'svelte/transition'
import Detail from './Detail.svelte'
import Vote from './Vote.svelte'

let token = localStorage.getItem('memetoken');
const username = token.split('-')[1];

let memes = [];
let selected = null;

let timer = null;
let lastMouseMove = new Date();
function mousemove() {
	delayRankRecalculation();
	lastMouseMove = new Date();
}

function delayRankRecalculation() {
	if(timer) {
		clearInterval(timer);
	}
	timer = setTimeout(() => {
		reposition();
		timer = null;
	}, 1000);
}

function reposition() {
	memes = [...memes].sort((a, b) => a.rank - b.rank);
}

const evt = new EventSource('events');
evt.onmessage = function(data) {
	const first = memes.length == 0;

	const newMemes = JSON.parse(data.data);
	const ranking = [...new Set(newMemes.map(meme => meme.liked.length))].sort((a, b) => b - a);
	for(const meme of newMemes) {
		const idx = memes.findIndex(item => item.author == meme.author);
		if(idx >= 0) {
			memes[idx] = meme;
		} else {
			memes.push(meme);
		}
	}

	memes = memes.map(meme => {
		meme.rank = ranking.indexOf(meme.liked.length) + 1;
		if(meme.author == 'TRN0038') {
			meme.rank = 10000;
		}
		return meme;
	});
	if(first) {
		reposition();
	}
	delayRankRecalculation();
}

</script>
<style>

@font-face {
	font-family: 'Impact';
	src: url('Impact.TTF');
}

h1 {
	font-family: Impact;
	font-weight: normal;
	font-size: 50px;
	margin: 0px;
	text-transform: uppercase;
	text-align: center;
	-webkit-text-stroke: 2px black;
	color: white;
	text-align: center;
}
h1 img {
	height: 100px;
}

.memes {
	display: flex;
	flex-wrap: wrap;
	justify-content: center;
}
div.meme {
	margin-bottom: 20px;
	margin-right: 20px;
}
div > img {
	height: 400px;
	cursor: pointer;
}
</style>

{#if selected}
	<Detail meme={memes.find(meme => meme.author == selected)} {username} bind:selected={selected} />
{/if}

<div class="container">
	<h1>
		Best meme ever contest
		<img src="accepted.png">
	</h1>
	<div class="memes">
	{#each memes as meme (meme.author)}
		<div class="meme" id="meme-{meme.author}" animate:flip="{{duration: 500}}">
			<div style="display: flex; justify-content:space-between; font-size: 1.5rem">
				<div>#{meme.rank}</div>
				<div>by {meme.author}</div>
			</div>
			<img src="{meme.path}" on:click={() => selected = meme.author}>
			<Vote meme={meme} {username} />
		</div>
	{/each}
	</div>
</div>
