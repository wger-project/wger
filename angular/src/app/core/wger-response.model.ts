
/*
 * Interface for a response from the API (if no errors occur)
 */
export interface WgerApiResponse<Type> {
  count: number;
  next: string;
  previous: string;
  results: Type[];
}
