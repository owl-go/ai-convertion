async function request(path, options = {}) {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "请求失败");
  return body;
}
export const listTasks = (includeDone = false) => request(`/api/tasks?include_done=${includeDone ? "1" : "0"}`);
export const createTask = (title) => request("/api/tasks", {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title })
});
export const completeTask = (id) => request(`/api/tasks/${id}/complete`, { method: "POST" });
