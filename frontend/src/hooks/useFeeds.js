import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

export function useFeeds() {
  return useQuery({
    queryKey: ['feeds'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/feeds/');
      return data;
    },
  });
}

export function useCreateFeed() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (feedData) => {
      const { data } = await apiClient.post('/api/feeds/', feedData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
    },
  });
}
