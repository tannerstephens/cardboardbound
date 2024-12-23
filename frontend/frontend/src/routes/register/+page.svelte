<script lang="ts">
	import { api } from '$lib';
	import { getToastStore, type ToastSettings } from '@skeletonlabs/skeleton';

	let username: string,
		password: string,
		invite: string,
		submitDisabled: boolean = true;

	const toastStore = getToastStore();

	const validate = () => {
		submitDisabled = username.length === 0 || password.length === 0 || invite.length === 0;
	};

	const submit = () => {
		if (submitDisabled) {
			return;
		}

		api
			.register(username, password, invite)
			.then((resp) => resp.json())
			.then((json) => {
				if (json.success) {
					window.location.assign('/');
				} else {
					const t: ToastSettings = {
						message: json.error_message,
						background: 'variant-filled-error'
					};
					toastStore.trigger(t);
				}
			});
	};
</script>

<div class="container mx-auto px-4 max-w-3xl">
	<form on:submit|preventDefault={submit}>
		<div class="card p-4 my-2 space-y-4">
			<h1>Register</h1>
			<label class="label">
				<span>Username</span>
				<input
					class="input"
					type="text"
					placeholder="Username"
					bind:value={username}
					on:input={validate}
				/>
			</label>

			<label class="label">
				<span>Password</span>
				<input
					class="input"
					type="password"
					placeholder="Password"
					bind:value={password}
					on:input={validate}
				/>
			</label>

			<label class="label">
				<span>Invite Code</span>
				<input
					class="input"
					type="text"
					placeholder="aaaaaaaa"
					bind:value={invite}
					on:input={validate}
				/>
			</label>

			<button type="submit" class="btn variant-filled" disabled={submitDisabled}> Login </button>
		</div>
	</form>
</div>
