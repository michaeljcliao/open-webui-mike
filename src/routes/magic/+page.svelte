<script lang="ts">
	import { onMount, getContext, tick } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	// import { page } from '$app/stores';
	import { config, user, socket } from '$lib/stores';
	import { getBackendConfig } from '$lib/apis';

	import { userMagicLinkSignIn } from '$lib/apis/auths';

    const i18n = getContext('i18n');

	const querystringValue = (key) => {
		const querystring = window.location.search;
		const urlParams = new URLSearchParams(querystring);
		return urlParams.get(key);
	};

	const setSessionUser = async (sessionUser) => {
		if (sessionUser) {
			console.log(sessionUser);
			toast.success($i18n.t(`You're now logged in.`));
			if (sessionUser.token) {
				localStorage.token = sessionUser.token;
			}

			$socket.emit('user-join', { auth: { token: sessionUser.token } });
			await user.set(sessionUser);
			await config.set(await getBackendConfig());

			const redirectPath = querystringValue('redirect') || '/';
			goto(redirectPath);
		}
	};

	onMount(async () => {
		const magic_token = querystringValue('magic_token');
		console.log('Magic token:', magic_token);
		if (!magic_token) {
			toast.error('Missing magic link token');
			console.error('Missing magic link token');
			await tick();
			await new Promise(r => setTimeout(r, 1000));
			// goto('/');
			return;
		}

		let sessionUser = null;
		try {
			sessionUser = await userMagicLinkSignIn(magic_token);
			console.log('Magic login successful:', sessionUser);
		} catch (error) {
			console.error('Magic login API error:', error);
			toast.error('Magic login error');
			await tick();
			await new Promise(r => setTimeout(r, 1000));
			// goto('/');
			return;
		}

		if (!sessionUser) {
			toast.error('Magic login failed.');
			console.error('Magic login failed.');
			await tick();
			await new Promise(r => setTimeout(r, 1000));
			// goto('/');
			return;
		}

		await setSessionUser(sessionUser);
	});
</script>

<p class="text-center mt-10">Logging you in with magic link...</p>
