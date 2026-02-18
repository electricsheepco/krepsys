import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

export function useArticles(filters = {}) {
  const queryParams = new URLSearchParams();
  if (filters.feed_id) queryParams.append('feed_id', filters.feed_id);
  if (filters.is_read !== undefined) queryParams.append('is_read', filters.is_read);
  if (filters.is_saved !== undefined) queryParams.append('is_saved', filters.is_saved);
  if (filters.is_archived !== undefined) queryParams.append('is_archived', filters.is_archived);
  if (filters.sort) queryParams.append('sort', filters.sort);

  return useQuery({
    queryKey: ['articles', filters],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/articles/?${queryParams}`);
      return data;
    },
  });
}

export function useArticle(id) {
  return useQuery({
    queryKey: ['article', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/articles/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useUpdateArticle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, updates }) => {
      const { data } = await apiClient.patch(`/api/articles/${id}/`, updates);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
    },
  });
}
