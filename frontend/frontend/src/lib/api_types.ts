export type Submission = {
	assignee: number | null;
	description: string | null;
	resolved: boolean;
	reviewed: boolean;
	title: string;
};

export type SubmissionResponse = {
	success: boolean;
	error_message: string;
	page: {
		items: Array<Submission>;
		next_page: number | null;
		page_count: number;
		previous_page: number | null;
	};
};
