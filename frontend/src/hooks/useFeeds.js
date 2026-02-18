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

export function useDeleteFeed() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (feedId) => {
      await apiClient.delete(`/api/feeds/${feedId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
    },
  });
}

export function useAllTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/articles/tags/all');
      return data;
    },
  });
}

export function useArticleTags(articleId) {
  const queryClient = useQueryClient();
  const add = useMutation({
    mutationFn: async (name) => {
      const { data } = await apiClient.post(`/api/articles/${articleId}/tags`, { name });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });
  const remove = useMutation({
    mutationFn: async (name) => {
      const { data } = await apiClient.delete(`/api/articles/${articleId}/tags/${name}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', articleId] });
    },
  });
  return { add, remove };
}
