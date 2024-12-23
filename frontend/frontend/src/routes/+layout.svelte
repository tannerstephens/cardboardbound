<script lang="ts">
	import '../app.postcss';
	import {
		AppShell,
		AppBar,
		LightSwitch,
		initializeStores,
		Toast,
		autoModeWatcher,
		modeCurrent,
		setInitialClassState
	} from '@skeletonlabs/skeleton';

	import { logo } from '$lib';
	import { api } from '$lib';

	import { onMount } from 'svelte';
	initializeStores();

	interface User {
		username: string;
	}

	let me: User | null = null;

	onMount(() => {
		autoModeWatcher();

		modeCurrent.set(window.localStorage.getItem('modeUserPrefers') == 'true');
		setInitialClassState();

		api
			.me()
			.then((resp) => resp.json())
			.then((json) => {
				me = json.item;
			});
	});

	const logout = () => {
		api.logout();
		me = null;
	};
</script>

<Toast position="t" />

<AppShell>
	<svelte:fragment slot="header">
		<AppBar>
			<svelte:fragment slot="lead">
				<a href="/"
					><img
						src={logo}
						alt="Cardboard Bound"
						title="Go to homepage"
						class="h-12 dark:invert"
					/></a
				>
			</svelte:fragment>

			<svelte:fragment slot="trail">
				{#if me === null}
					<a href="/login" class="btn hover:variant-soft-primary">Login</a>
					<a href="/register" class="btn hover:variant-soft-primary">Register</a>
				{:else}
					<button class="btn hover:variant-soft-primary" on:click={logout}>Logout</button>
				{/if}
				<LightSwitch />
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>

	<slot />
</AppShell>
