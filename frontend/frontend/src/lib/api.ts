export const BASE_API_ROUTE = '/api';

export default {
	submit: (title: string, description: string | null) =>
		fetch(`${BASE_API_ROUTE}/submissions`, {
			method: 'POST',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ title, description })
		}),
	login: (username: string, password: string) =>
		fetch(`${BASE_API_ROUTE}/session`, {
			method: 'POST',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		}),
	register: (username: string, password: string, invite: string) =>
		fetch(`${BASE_API_ROUTE}/users`, {
			method: 'POST',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password, invite })
		}),
	me: () => fetch(`${BASE_API_ROUTE}/session`),
	logout: () =>
		fetch(`${BASE_API_ROUTE}/session`, {
			method: 'DELETE'
		})
};
