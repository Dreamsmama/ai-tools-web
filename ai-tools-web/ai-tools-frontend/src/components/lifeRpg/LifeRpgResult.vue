<script setup>
import { computed } from 'vue'
import AttributePanel from './AttributePanel.vue'
import QuestCard from './QuestCard.vue'
import TaskItemCard from './TaskItemCard.vue'
import ProgressCard from './ProgressCard.vue'
import { collectAllTasks } from '../../lib/lifeRpgNormalize.js'

const props = defineProps({
  profile: { type: Object, default: null },
  result: { type: Object, required: true },
  attributes: { type: Object, required: true },
  completedTaskIds: { type: Array, default: () => [] },
  rawFallback: { type: String, default: '' },
})

const emit = defineEmits(['regenerate', 'edit-today', 'back-home', 'copy', 'toggle-task'])

const worldState = computed(() => props.result?.world_state || {})
const mainQuest = computed(() => props.result?.main_quest || {})
const mainTasks = computed(() => mainQuest.value.tasks || [])
const sideQuests = computed(() => props.result?.side_quests || [])
const notRecommend = computed(() => props.result?.not_recommend || [])

const allTasks = computed(() => collectAllTasks(props.result))
const completedCount = computed(() => {
  const set = new Set(props.completedTaskIds)
  return allTasks.value.filter((t) => set.has(t.id)).length
})
const totalCount = computed(() => allTasks.value.length)

function isCompleted(taskId) {
  return props.completedTaskIds.includes(taskId)
}
</script>

<template>
  <div class="result">
    <section v-if="rawFallback" class="tool-card tool-card--warn parse-warn">
      <h2 class="block-title">未能生成完整安排</h2>
      <p class="world-hint">AI 返回格式异常，请点击下方「重新生成今日安排」再试一次。</p>
      <pre v-if="rawFallback.length > 20" class="raw-text">{{ rawFallback }}</pre>
      <div class="actions actions--warn">
        <button type="button" class="btn btn-gradient" @click="emit('regenerate')">重新生成今日安排</button>
        <button type="button" class="btn-outline" @click="emit('edit-today')">修改今日状态</button>
      </div>
    </section>

    <template v-else>
    <section v-if="profile" class="tool-card tool-card--soft">
      <p class="kicker">你的角色路线</p>
      <h2 class="route-title">{{ profile.routeTitle }}</h2>
      <p class="route-summary">{{ profile.routeSummary }}</p>
      <p v-if="result.route_continuation" class="route-continuation">{{ result.route_continuation }}</p>
    </section>

    <AttributePanel :attributes="attributes" />

    <section class="tool-card tool-card--soft">
      <h2 class="block-title">今日状态</h2>
      <p class="world-hint">
        根据你的长期路线与今日状态，AI 已判断今天适合怎样推进。按你的节奏完成即可。
      </p>
      <h3 class="world-title">{{ worldState.title || '今日安排' }}</h3>
      <p class="world-desc">{{ worldState.description }}</p>
    </section>

    <ProgressCard :completed="completedCount" :total="totalCount" />

    <section class="tool-card">
      <h2 class="block-title">今日主线任务</h2>
      <QuestCard
        :title="mainQuest.title"
        :goal="mainQuest.goal"
        :estimated-time="mainQuest.estimated_time"
      />
      <TaskItemCard
        v-for="task in mainTasks"
        :key="task.id"
        :task="task"
        variant="main"
        :completed="isCompleted(task.id)"
        @toggle="emit('toggle-task', task.id)"
      />
    </section>

    <section v-if="sideQuests.length" class="tool-card">
      <h2 class="block-title">支线任务</h2>
      <TaskItemCard
        v-for="sq in sideQuests"
        :key="sq.id"
        :task="{ ...sq, estimated_time: '' }"
        variant="side"
        :completed="isCompleted(sq.id)"
        @toggle="emit('toggle-task', sq.id)"
      />
    </section>

    <section v-if="notRecommend.length" class="tool-card tool-card--warn">
      <h2 class="block-title">今日不建议</h2>
      <ul class="bullet-list">
        <li v-for="(item, idx) in notRecommend" :key="idx">{{ item }}</li>
      </ul>
    </section>

    <section v-if="result.ending" class="tool-card ending-card">
      <p class="ending">{{ result.ending }}</p>
    </section>

    <div class="actions">
      <button type="button" class="btn btn-gradient" @click="emit('regenerate')">重新生成今日安排</button>
      <button type="button" class="btn-outline" @click="emit('edit-today')">修改今日状态</button>
      <button type="button" class="btn-outline" @click="emit('copy')">复制安排</button>
      <button type="button" class="btn-outline" @click="emit('back-home')">返回我的人生路线</button>
    </div>
    </template>
  </div>
</template>

<style scoped>
.result {
  display: flex;
  flex-direction: column;
}

.parse-warn .actions--warn {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.parse-warn .actions--warn .btn-gradient,
.parse-warn .actions--warn .btn-outline {
  width: 100%;
}
</style>
