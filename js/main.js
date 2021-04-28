import App from './App.svelte';

const token = (new URL(document.location.href)).searchParams.get('token');
if(token) {
	localStorage.setItem('memetoken', token);
	document.location.href='./';
}
if(!localStorage.getItem('memetoken')) {
	document.location.href = '/';
}


var app = new App({
	target: document.body
});

export default app;
