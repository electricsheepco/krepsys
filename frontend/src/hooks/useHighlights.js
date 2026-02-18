import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

export function useHighlights(articleId) {
  return useQuery({
    queryKey: ['highlights', articleId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/articles/${articleId}/highlights`);
      return data;
    },
    enabled: !!articleId,
  });
}

export function useCreateHighlight(articleId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await apiClient.post(`/api/articles/${articleId}/highlights`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['highlights', articleId] });
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
    },
  });
}

export function useDeleteHighlight(articleId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (highlightId) => {
      await apiClient.delete(`/api/articles/highlights/${highlightId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['highlights', articleId] });
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
    },
  });
}
