<script lang="ts">
	import { api } from '$lib';
	import { page } from '$app/state';

	import { type Submission } from '$lib/api_types';

	import { Paginator, type PaginationSettings } from '@skeletonlabs/skeleton';
	import { goto } from '$app/navigation';

	import { onMount } from 'svelte';

	let pageNum = Number(page.url.searchParams.get('p') || 1);
	let perPage = Number(page.url.searchParams.get('per_page') || 15);

	let submissions: Array<Submission> = [],
		size = 0;

	let paginationSettings: PaginationSettings;

	$: paginationSettings = {
		page: pageNum - 1,
		limit: perPage,
		size: size,
		amounts: [12, 24, 48, 60]
	} satisfies PaginationSettings;

	const loadSubmissions = () => {
		api.submissions(pageNum, perPage).then((json) => {
			if (!json.success) {
				return;
			}

			size = json.page.page_count * perPage;
			submissions = json.page.items;
		});
	};

	onMount(loadSubmissions);

	const onPageChange = (e: CustomEvent) => {
		pageNum = e.detail + 1;

		page.url.searchParams.set('p', pageNum.toString());
		goto(`?${page.url.searchParams.toString()}`);
		loadSubmissions();
	};

	const onAmountChange = (e: CustomEvent) => {
		perPage = e.detail;

		page.url.searchParams.set('per_page', perPage.toString());
		goto(`?${page.url.searchParams.toString()}`);
		loadSubmissions();
	};
</script>

<div class="container mx-auto">
	<div class="grid grid-cols-1 lg:grid-cols-3 md:grid-cols-2 gap-4 my-4">
		{#each submissions as submission}
			<div class="card p-4">
				<header class="card-header">
					<h1 class="text-5xl font-extrabold dark:text-white">{submission.title}</h1>
				</header>
				<section class="p-4 break-words"><div>{submission.description}</div></section>
			</div>
		{/each}
	</div>

	<Paginator
		bind:settings={paginationSettings}
		showFirstLastButtons={false}
		showPreviousNextButtons={true}
		on:page={onPageChange}
		on:amount={onAmountChange}
	/>
</div>
