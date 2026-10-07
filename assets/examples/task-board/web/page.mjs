import { listTasks, createTask, completeTask } from "./api.mjs";

const form = document.querySelector("form");
const input = document.querySelector("#title");
const submit = document.querySelector("#submit");
const status = document.querySelector("#status");
const list = document.querySelector("#tasks");

async function load() {
  status.textContent = "加载中…";
  try {
    const tasks = await listTasks();
    list.replaceChildren();
    for (const task of tasks) {
      const item = document.createElement("li");
      const label = document.createElement("span");
      label.textContent = `${task.title} · ${task.done ? "已完成" : "待完成"}`;
      item.append(label);
      if (!task.done) {
        const button = document.createElement("button");
        button.textContent = "完成";
        button.setAttribute("aria-label", `完成任务：${task.title}`);
        button.onclick = async () => {
          button.disabled = true;
          try { await completeTask(task.id); await load(); }
          catch (error) { status.textContent = error.message; button.disabled = false; }
        };
        item.append(button);
      }
      list.append(item);
    }
    status.textContent = tasks.length ? `共 ${tasks.length} 个任务` : "暂无任务，添加第一个任务。";
  } catch (error) { status.textContent = `${error.message}，可点击重试。`; }
}
form.onsubmit = async (event) => {
  event.preventDefault();
  submit.disabled = true;
  status.textContent = "提交中…";
  try { await createTask(input.value); input.value = ""; await load(); input.focus(); }
  catch (error) { status.textContent = error.message; }
  finally { submit.disabled = false; }
};
document.querySelector("#retry").onclick = load;
load();
