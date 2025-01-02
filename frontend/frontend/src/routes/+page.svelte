<script lang="ts">
	import { faHeartPulse } from '@fortawesome/free-solid-svg-icons';
	import { getToastStore, type ToastSettings } from '@skeletonlabs/skeleton';
	import Fa from 'svelte-fa';

	import { api } from '$lib';

	let gameTitle: string,
		description: string,
		submitDisabled: boolean = true;

	const toastStore = getToastStore();

	const validate = () => {
		submitDisabled = gameTitle.length === 0;
	};
	const submit = () => {
		if (submitDisabled) {
			return;
		}

		api
			.submit(gameTitle, description)
			.then((resp) => resp.json())
			.then((json) => {
				if (json.success) {
					gameTitle = '';
					description = '';
					submitDisabled = true;

					const t: ToastSettings = {
						message: 'Thank you for your submission!',
						background: 'variant-filled-success'
					};
					toastStore.trigger(t);
				} else {
					const t: ToastSettings = {
						message: json.errors.join("\n"),
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
			<label class="label">
				<span>Game Title</span>
				<input
					class="input"
					type="text"
					placeholder="Monopoly"
					bind:value={gameTitle}
					on:input={validate}
				/>
			</label>

			<label class="label">
				<span>Issue Description</span>
				<textarea
					class="textarea"
					rows="5"
					placeholder="Park Place is ripped in half"
					bind:value={description}
					on:input={validate}
				/>
			</label>

			<button type="submit" class="btn variant-filled" disabled={submitDisabled}>
				<span><Fa icon={faHeartPulse} /></span>
				<span>Submit Issue</span>
			</button>
		</div>
	</form>
</div>
