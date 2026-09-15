|Company|Product / representative work|Sub-scenario|Improvement target / artifact|AI-controlled part|RSI relation||
|A. Frontier foundation-model & general-agent labs  Broad model/platform labs; RSI appears as one capability frontier rather than the sole company thesis.|
|OpenAI|Research acceleration / automated research intern|AI-for-AI research|research code; experiments; evals|code; experiments; candidate integration|L2|[](https://openai.com/index/research-acceleration-view-inside-openai/)|
||GPT-Red|self-play robustness|red-team policy; adversarial data|attack; defend; train; evaluate|L2|[](https://openai.com/index/unlocking-self-improvement-gpt-red/)|
||Self-improving tax agents|production adaptation|agent code; prompts; eval set|mine failures; patch; evaluate|L4 cand.|[](https://openai.com/index/building-self-improving-tax-agents-with-codex/)|
||Harness Engineering|agent-first software R&D|repo; CI; agent instructions|code; test; PR; repair|L1-L2 adj.|[](https://openai.com/index/harness-engineering/)|
||Symphony|agent orchestration|task state; repo; workflows|schedule; execute; handoff|L1 adj.|[](https://github.com/openai/symphony)|
||AgentKit / prompt optimizer / RFT|agent optimization stack|prompts; graders; weights|optimize; grade; fine-tune|L1-L2|[](https://openai.com/index/introducing-agentkit/)|
||Deep Research|autonomous research|task-local evidence|search; browse; synthesize|B0|[](https://openai.com/index/introducing-deep-research/)|
|Anthropic|When AI builds itself|RSI roadmap|AI-development process|code; experiments; future successor design|L5 target|[](https://www.anthropic.com/institute/recursive-self-improvement)|
||Automated Weak-to-Strong Researcher|automated alignment research|hypotheses; code; experiment logs|propose; train; evaluate; share|L2|[](https://alignment.anthropic.com/2026/automated-w2s-researcher/)|
||Tool optimization with Claude|tool self-optimization|tool specs; implementations|analyze traces; rewrite; evaluate|L2|[](https://www.anthropic.com/engineering/writing-tools-for-agents)|
||Harness design for long-running apps|autonomous software R&D|harness; evaluator; app code|plan; generate; evaluate; iterate|L2 adj.|[](https://www.anthropic.com/engineering/harness-design-long-running-apps)|
||Effective long-running agent harnesses|cross-context persistence|progress files; git state|initialize; code; handoff|L1 adj.|[](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)|
||Agent Skills|persistent skill substrate|skills; scripts; resources|discover; load; reuse|L1 enabler|[](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)|
||Multi-agent Research|autonomous research|task-local findings|plan; spawn; search; synthesize|B0|[](https://www.anthropic.com/engineering/multi-agent-research-system)|
||Managed Agents|long-horizon agent infrastructure|stable interface; harness|run; resume; supervise|L1 enabler|[](https://www.anthropic.com/engineering/managed-agents)|
||Parallel Claude compiler project|autonomous software engineering|shared codebase; tests|decompose; code; test; coordinate|B0-L1 adj.|[](https://www.anthropic.com/engineering/building-c-compiler)|
|Google DeepMind|AlphaEvolve|task-specific program search|algorithms; kernels; system code|generate; mutate; evaluate; select|B0|[](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)|
||AI Co-Scientist|scientific hypothesis search|hypotheses; research proposals|generate; debate; rank; refine|L2 adj.|[](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/)|
||AlphaChip|AI-for-hardware co-design|chip layouts; design policy|place; score; learn; transfer|L2 adj.|[](https://deepmind.google/blog/how-alphachip-transformed-computer-chip-design/)|
|NVIDIA|Eureka|reward / policy design|reward code; robot policies|reward synthesis; simulation; policy training|L2|[](https://arxiv.org/abs/2310.12931)|
||ASPIRE|reward / policy design|reward code; robot policies|reward synthesis; simulation; policy training|L2|[](https://research.nvidia.com/labs/gear/aspire/)|
|Microsoft|Agent Lightning|agent reinforcement learning|policy weights; experience traces|collect; credit; train; evaluate|L2|[](https://www.microsoft.com/en-us/research/project/agent-lightning/)|
||Agent Lightning v1.0|harnessed agentic RL|harness traces; policy weights|interact; retokenize; train; benchmark|L2|[](https://www.microsoft.com/en-us/research/publication/agent-lightning-v1-0-towards-harnessed-agentic-rl/)|
||SkillOpt|skill optimization|skill files; instructions|edit; evaluate; optimize|L2|[](https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters/)|
||ReVeal|self-verifying code agents|code; tests; verifier policy|generate; verify; revise; scale|L2|[](https://www.microsoft.com/en-us/research/publication/reveal-self-evolving-code-agents-via-reliable-self-verification/)|
||Universal Verifier / auto-research|agent verification R&D|rubrics; verifier; eval pipeline|design; test; compare; refine|L2 adj.|[](https://www.microsoft.com/en-us/research/articles/the-art-of-building-verifiers-for-computer-use-agents/)|
|Meta|Self-Taught Evaluator|evaluator self-training|judge model; synthetic preferences|generate; judge; train; iterate|L2|[](https://ai.meta.com/blog/fair-news-segment-anything-2-1-meta-spirit-lm-layer-skip-salsa-lingua/)|
||HyperAgents|meta-agent self-modification|task agent; meta agent; program|solve; self-edit; evaluate; archive|L5 cand.|[](https://ai.meta.com/research/publications/hyperagents/)|
|Alibaba / Qwen|Qwen-Agent|agent training / synthetic environments|training data; environments; post-training|simulation; data synthesis; tool use; RL|L1-L2|[](https://qwenlm.github.io/blog/qwen-agent-2405/)|
||AgentWorld|agent training / synthetic environments|training data; environments; post-training|simulation; data synthesis; tool use; RL|L1-L2|[](https://qwen.ai/blog?id=qwen-agentworld)|
||Qwen-Scope|agent training / synthetic environments|training data; environments; post-training|simulation; data synthesis; tool use; RL|L1-L2|[](https://arxiv.org/abs/2605.11887)|
|DeepSeek|R1|reasoning self-bootstrapping|reasoning policy; verifier|self-generated reasoning; RL; verifier iteration|L2|[](https://github.com/deepseek-ai/DeepSeek-R1)|
||Math-V2|reasoning self-bootstrapping|reasoning policy; verifier|self-generated reasoning; RL; verifier iteration|L2|[](https://github.com/deepseek-ai/DeepSeek-Math-V2)|
|Tencent AI Lab|R-Zero|self-play reasoning|tasks; pseudo-labels; policy weights|challenge generation; solve; vote; RL|L2-L3|[](https://arxiv.org/abs/2508.05004)|
|ByteDance Seed|Seed-Thinking|model / agent post-training|data; reward; policy weights|data filtering; reward verification; RL|L1-L2|[](https://github.com/ByteDance-Seed)|
||Seed1.5-VL|model / agent post-training|data; reward; policy weights|data filtering; reward verification; RL|L1-L2|[](https://seed.bytedance.com/zh/blog/bytedance-s-latest-thinking-model-seed-thinking-v1-5-technical-details-disclosed)|
|MiniMax|M2|persistent cloud agents|memory; skills; agent policy|tool use; long-run execution; skill reuse|L1-L2|[](https://www.minimax.io/news/minimax-m2)|
||MaxHermes|persistent cloud agents|memory; skills; agent policy|tool use; long-run execution; skill reuse|L1-L2|[](https://www.maxhermes.dev/en)|
||MaxClaw|persistent cloud agents|memory; skills; agent policy|tool use; long-run execution; skill reuse|L1-L2|[](https://agent.minimaxi.com/activity/max-claw)|
|Moonshot AI|Kimi K3|long-horizon agents|agent orchestration; tool policy|planning; tool use; swarm coordination|L1-L2 adj.|[](https://www.moonshot.cn/)|
||Agent Swarm|long-horizon agents|agent orchestration; tool policy|planning; tool use; swarm coordination|L1-L2 adj.|[](https://www.moonshot.cn/)|
|Zhipu AI / Z.AI|AutoGLM|computer-use agent training|policy weights; virtual-phone environments|perception; planning; action; RL|L2|[](https://autoglm.z.ai/blog/)|
||AgentRL|computer-use agent training|policy weights; virtual-phone environments|perception; planning; action; RL|L2|[](https://docs.z.ai/guides/vlm/autoglm-phone-multilingual)|
|Deep Cogito|Cogito v2|reasoning post-training|reasoning policy; weights|search; distill; iterative alignment|L1-L2|[](https://www.deepcogito.com/research/cogito-v2-preview)|
||IDA|reasoning post-training|reasoning policy; weights|search; distill; iterative alignment|L1-L2|[](https://www.deepcogito.com/research/cogito-v2-1)|
|Poolside|Model Factory|automated model R&D|synthetic data; RL; architecture|eval; code-exec RL; ablations; data mix|L1-L2|[](https://poolside.ai/research)|
|Thinking Machines Lab|Tinker Agent RL|model customization / agent RL|policy weights; tool-use policy|RL; LLM-judge grading; tool discovery|L1-L2|[](https://tinker-docs.thinkingmachines.ai/cookbook/recipes/agent-rl/)|
||Inkling|model customization / agent RL|policy weights; tool-use policy|RL; LLM-judge grading; tool discovery|L1-L2|[](https://thinkingmachines.ai/news/introducing-inkling/)|
|Nous Research|Hermes Agent|persistent agents|skills; memory; tool gateway|memory; skill reuse; tool orchestration|L1-L2|[](https://github.com/NousResearch/hermes-agent)|
||skills / memory|persistent agents|skills; memory; tool gateway|memory; skill reuse; tool orchestration|L1-L2|[](https://hermes-agent.nousresearch.com/docs)|
|B. RSI-native / AI4AI companies  Self-improvement, AI-for-AI, self-evolution, or recursive improvement is central to the company/research thesis.|
|Ricursive Intelligence|AI-chip co-design|AI systems / chips|EDA designs; compute stack|design search; verify; iterate|L2; L5 vision|[](https://www.ricursive.com/)|
|Recursive|Automated AI Research|model-training research|training recipes; kernels; code|ideas; experiments; branch merge|L2|[](https://www.recursive.com/articles/first-steps-toward-automated-ai-research)|
|Imbue|Catalyst|research search|recipes; code; hypotheses|population search; experiments; interpretation|L2-L3|[](https://github.com/imbue-ai/catalyst)|
||Darwinian Evolver|research search|recipes; code; hypotheses|population search; experiments; interpretation|L2-L3|[](https://imbue.com/blog/2026-07-20-imbue-catalyst-nanochat)|
|Weco AI|AIDE2|meta-improvement of researcher|research harness; improver code|rewrite improver; eval; inheritance|L5 cand.|[](https://www.weco.ai/blog/first-evidence-of-recursive-self-improvement)|
|Sakana AI|Darwin Godel Machine|self-editing agents / AI research|agent source; research pipeline|self-modify; benchmark; archive; experiments|L5 cand.|[](https://arxiv.org/abs/2505.22954)|
||AI Scientist|self-editing agents / AI research|agent source; research pipeline|self-modify; benchmark; archive; experiments|L5 cand.|[](https://github.com/SakanaAI/AI-Scientist)|
|Evolvent AI|Org self-evolving agents|software-agent evolution|skills; memory; code; environments|tasks; feedback; refactor; skill updates|L2-L3|[](https://evolvent.co/zh/blog/org-self-evolving-agents)|
||RSIBench|software-agent evolution|skills; memory; code; environments|tasks; feedback; refactor; skill updates|L2-L3|[](https://evolvent.co/zh/blog/RSIBench-Data)|
||Terrarium|software-agent evolution|skills; memory; code; environments|tasks; feedback; refactor; skill updates|L2-L3|[](https://evolvent.co/en/blog/terrarium)|
|MetaCircle|ComfyResearch|AI4AI / autoresearch|training workflows; research hypotheses|experiment compose; code; hypothesis; scoring|L2; L5 vision|[](https://meta-circle.com/blog/comfyresearch-see-how-learning-happens)|
||OPHIS|AI4AI / autoresearch|training workflows; research hypotheses|experiment compose; code; hypothesis; scoring|L2; L5 vision|[](https://meta-circle.com/blog/ophis-a-new-paradigm-for-autoresearch)|
|Frontis AI / Xianyuan|OpenRSI|AI4AI / self-improving agents|skills; memory; harness; weights|experience; update search; eval; post-training|L2-L3|[](https://github.com/FrontisAI/OpenRSI)|
||Frontis-MA1|AI4AI / self-improving agents|skills; memory; harness; weights|experience; update search; eval; post-training|L2-L3|[](https://arxiv.org/abs/2607.28568)|
|EvoMap|Evolver|shared code evolution|genes / capsules; code assets|generate; test; publish; reuse; adapt|L2-L3|[](https://github.com/EvoMap/evolver)|
||GEP|shared code evolution|genes / capsules; code assets|generate; test; publish; reuse; adapt|L2-L3|[](https://evomap.ai/wiki/16-gep-protocol)|
||GeneBench|shared code evolution|genes / capsules; code assets|generate; test; publish; reuse; adapt|L2-L3|[](https://evomap.ai/wiki/36-gene-bench-report)|
|Endless Frontier|BigBang-v1|AI-research data generation|synthetic programs; training data; critic|generate; execute; critique; meta-critique|L2-L3|[](https://github.com/endless-frontier/BigBang-v1)|
|Mirendil|Self-accelerating AI|AI R&D automation|model code; experiments; research stack|experiment generation; execution; iteration|L2|[](https://mirendil.com/news/scaling-self-accelerating-ai-with-google/)|
||AI Scientist|AI R&D automation|model code; experiments; research stack|experiment generation; execution; iteration|L2|[](https://www.devvrit.com/)|
|Chaoyan Intelligence\*|TUMIX|self-evolving research models|research policy; tool-use policy|questioning; experiments; code; self-check|L2-L3|[](https://arxiv.org/abs/2510.01279)|
||R1-Code-Interpreter|self-evolving research models|research policy; tool-use policy|questioning; experiments; code; self-check|L2-L3|[](https://arxiv.org/abs/2505.21668)|
||AI Scientist|self-evolving research models|research policy; tool-use policy|questioning; experiments; code; self-check|L2-L3|[](https://www.qbitai.com/2026/07/455041.html)|
|Theseus|Argus|long-horizon self-evolving agents|experience; memory; environment setup|plan; code; review; experience writeback|L2-L3|[](https://arxiv.org/abs/2608.05144)|
||SetupX|long-horizon self-evolving agents|experience; memory; environment setup|plan; code; review; experience writeback|L3|[](https://arxiv.org/abs/2605.26186)|
|Adaption Labs|AutoScientist|AI-research automation|training recipes; datasets; code|research plan; experiments; selection|L2|[](https://docs.adaptionlabs.ai/autoscientist/overview/)|
||Forge|AI-research automation|training recipes; datasets; code|research plan; experiments; selection|L2|[](https://docs.adaptionlabs.ai/api/resources/autoscientist)|
|C. Autonomous R&D & scientific-discovery companies  Primary product is automated research/discovery; RSI relevance comes from automating experiment and knowledge-production loops.|
|Periodic Labs|Autonomous laboratory|AI for science|hypotheses; experiment data; models|experiment design; lab run; learning|L3 cand.|[](https://periodic.com/)|
|FutureHouse|BixBench|AI-scientist evaluation|research tasks; benchmark frontier|bioinformatics workflows; open-ended eval|B0-L2 adj.|[](https://github.com/Future-House/BixBench)|
|Edison Scientific|Kosmos|autonomous science|hypotheses; code; scientific artifacts|literature; experiments; synthesis|L2-L3|[](https://arxiv.org/abs/2511.02824)|
|Axiom Math|Putnam 2025|formal mathematics|proofs; verifier traces|conjecture; proof search; formal verification|L2|[](https://github.com/AxiomMath/putnam2025)|
||IMO 2026|formal mathematics|proofs; verifier traces|conjecture; proof search; formal verification|L2|[](https://github.com/AxiomMath/IMO2026)|
|Harmonic|Aristotle|theorem proving|formal proofs|translate; prove; verify|L1-L2|[](https://harmonic.fun/pdf/Aristotle_IMO_Level_Automated_Theorem_Proving.pdf)|
|Core Automation|AI systems-research stack|automated systems research|systems code; research hypotheses|design; code; benchmark; iterate|L2 cand.|[](https://www.coreauto.com/blog)|
|Discovery Loop|Autonomous discovery loop|automated experimentation|protocols; findings|hypothesis; experiment; analysis; next-step|L3 cand.|[](https://www.discoveryloop.com/)|
|Lila Sciences|Autonomous Science platform|scientific discovery|hypotheses; experiments; post-training data|design; lab execution; real-time learning|L3 cand.|[](https://www.lila.ai/)|
|Karpathy / autoresearch|autoresearch|narrow automated research|training code; configs|edit; train; measure; keep|L2|[](https://github.com/karpathy/autoresearch)|
|Prime Intellect|Autonomous research|model R&D|training recipe; optimizer; code|hypothesis; GPU runs; ablation|L2|[](https://www.primeintellect.ai/blog/measuring-autonomous-research)|
||Speedrun Frontier|model R&D|training recipe; optimizer; code|hypothesis; GPU runs; ablation|L2|[](https://github.com/PrimeIntellect-ai/experiments-autonomous-speedrunning)|
|Analemma|FARS|autonomous research|proposals; code; logs; papers|topic; experiment; analysis; writing|L2-L3|[](https://fars-live.analemma.ai/blog/introducing-fars/)|
|Novix|AutoAgent|AI research agent|research workflow; eval harness|idea; tool use; experiments; reporting|L2|[](https://github.com/HKUDS/AutoAgent)|
||OpenHarness|AI research agent|research workflow; eval harness|idea; tool use; experiments; reporting|L2|[](https://github.com/HKUDS/OpenHarness)|
||AI-Researcher|AI research agent|research workflow; eval harness|idea; tool use; experiments; reporting|L2|[](https://github.com/HKUDS/AI-Researcher)|
|UniPat|UniScientist|research / evaluation agents|research traces; benchmarks|experiments; coding; multi-agent eval|L1-L2|[](https://www.unipat.ai/blog/UniScientist)|
||UniSwarm|research / evaluation agents|research traces; benchmarks|experiments; coding; multi-agent eval|L1-L2|[](https://www.unipat.ai/blog/UniSwarm)|
||UniMath|research / evaluation agents|research traces; benchmarks|experiments; coding; multi-agent eval|L1-L2|[](https://www.unipat.ai/blog/UniMath)|
|Kai Chen / venture TBD\*|Intern-S1|AI for science models|scientific model; training data|model training; scientific reasoning|adj.; entity TBD|[](https://air.tsinghua.edu.cn/info/1008/2492.htm)|
|D. Agent optimization, evaluation & learning infrastructure  Infrastructure for feedback, skills, RL, evaluation, simulators, training data, or production-agent improvement.|
|Warp|Skill optimization loop|coding-agent skills|skills; instructions; examples|feedback mining; skill rewrite; eval|L2|[](https://www.warp.dev/blog/self-improvement-loop-for-skills)|
|Factory|Signals|production coding agents|agent behavior; product code|session mining; failure clusters; patch PRs|L4|[](https://factory.com/news/factory-signals)|
||Software Factory|production coding agents|agent behavior; product code|session mining; failure clusters; patch PRs|L4|[](https://factory.ai/news/software-factory)|
|LangChain|LangSmith self-improving evaluators|evaluator alignment|judge prompts; evaluator model|feedback ingest; judge update; eval|L1-L2|[](https://docs.langchain.com/langsmith/improve-judge-evaluator-feedback)|
|Replit|Agent 3|software engineering|application code; tests|build; test; repair; long runs|L1-L2|[](https://replit.com/blog/introducing-agent-3-our-most-autonomous-agent-yet)|
|MorphMind|Caliper|agent calibration / org memory|agent skills; shared experience|measure; route; reuse experience|L1-L2 adj.|[](https://morphmind.ai/products/caliper)|
|DatologyAI|BeyondWeb|data optimization|training corpus; synthetic data|curate; filter; synthesize; benchmark|L1-L2|[](https://www.datologyai.com/blog/beyondweb)|
||DatBench|data optimization|training corpus; synthetic data|curate; filter; synthesize; benchmark|L1-L2|[](https://www.datologyai.com/blog/datbench-discriminative-faithful-and-efficient-vision-language-model-evaluations)|
|Ineffable Intelligence|RL infrastructure|RL / experience infrastructure|training environments; trajectories|rollouts; reward; distributed RL|L1-L3 enabler|[](https://www.ineffable.ai/)|
|Goodfire|Ember|interpretability-driven training|feature activations; reward signals|feature discovery; feedback; RL|L1-L2|[](https://www.goodfire.com/research/rlfr)|
||RLFR|interpretability-driven training|feature activations; reward signals|feature discovery; feedback; RL|L1-L2|[](https://www.goodfire.com/research/rlfr)|
|Patronus AI|Generative Simulators|evaluation / simulation|simulators; eval suites|scenario generation; grading; failure analysis|L2-L3 enabler|[](https://www.patronus.ai/blog/introducing-generative-simulators)|
||Percival|evaluation / simulation|simulators; eval suites|scenario generation; grading; failure analysis|L2-L3 enabler|[](https://www.patronus.ai/blog/percival-chat-an-eval-copilot-for-agentic-systems)|
|Braintrust|Loop|production feedback / eval|prompts; evals; datasets|trace ingest; scoring; prompt optimization|L1-L2|[](https://www.braintrust.dev/docs/loop)|
||Autoevals|production feedback / eval|prompts; evals; datasets|trace ingest; scoring; prompt optimization|L1-L2|[](https://www.braintrust.dev/docs/cookbook/recipes/Loop)|
|Mechanize|RL environments|experience / eval infrastructure|RL tasks; graders; environments|task design; grading; training signal|L3 enabler|[](https://www.mechanize.work/)|
||GBA Eval|experience / eval infrastructure|RL tasks; graders; environments|task design; grading; training signal|L3 enabler|[](https://www.mechanize.work/)|
|Kando AI|Early company signal|undisclosed / early-stage|undisclosed|undisclosed|unverified|[](https://www.preqin.com/data/profile/asset/kando-ai/811935)|
|Entropy Order\*|Data-expert platform|high-quality training data|expert data; eval assets|data production; benchmarking|L1-L3 enabler|[](https://emergeia.com/en/project/2025F-020)|
|Compounding Intelligence / CORAL\*|CORAL|multi-agent research|shared notes; skills; logs|parallel experiments; knowledge sharing; eval|L2-L3|[](https://human-agent-society.github.io/CORAL)|
|Naive.ai\*|Research-lab signal|early RSI lab|undisclosed|undisclosed|RSI claim; unverified|[](https://naive.ai/)|
|E. Embodied, world-model & continual-adaptation companies  Persistent adaptation is tied to world models, robotics, environments, or test-time/continual learning.|
|AI2 Robotics|FiS-VLA|embodied policy learning|VLA policy; action data|data; training; planning; control|L2-L3 adj.|[](https://arxiv.org/abs/2506.01953)|
||Video2Act|embodied policy learning|VLA policy; action data|data; training; planning; control|L2-L3 adj.|[](https://ai2robotics.com/about/)|
|X Square Robot|WALL|world models / skill acquisition|world model; skills; action policy|video skill capture; world prediction; control|L2-L3|[](https://x2robot.com/research)|
||HOST|world models / skill acquisition|world model; skills; action policy|video skill capture; world prediction; control|L2-L3|[](https://x2robot.com/pages/host)|
|Galaxea AI|G0 / G0.5|VLA R&D platform|VLA model; data; deployment stack|training; eval; real-robot deployment|L2 adj.|[](https://arxiv.org/abs/2509.00576)|
||GForge|VLA R&D platform|VLA model; data; deployment stack|training; eval; real-robot deployment|L2 adj.|[](https://galaxea-ai.com/cn/platform)|
|TARS Robotics|AWE|tactile world models|tactile world model; manipulation policy|multimodal sensing; prediction; control|L2-L3 adj.|[](https://capital.lenovo.com/news/detail/id/1092/s/1.html)|
||TacForeSight|tactile world models|tactile world model; manipulation policy|multimodal sensing; prediction; control|L2-L3 adj.|[](https://www.webdisclosure.com/press-release/tars-etr-tars-debuts-at-waic-2026-as-its-awe-embodied-foundation-model-wins-prestigious-sail-award-169FMrhkUg1)|
|Synapx Dynamics|SYNWorld|embodied data / model stack|data; world model; post-training|data synthesis; training; eval; control|L2-L3|[](https://www.synapxdynamics.ai/news/25)|
||OctoMind|embodied data / model stack|data; world model; post-training|data synthesis; training; eval; control|L2-L3|[](https://www.synapxdynamics.ai/news/46)|
||OctoSense|embodied data / model stack|data; world model; post-training|data synthesis; training; eval; control|L2-L3|[](https://www.synapxdynamics.ai/news/46)|
|MirrOS|Code as Worlds|world models / test-time adaptation|world code; fast weights|environment modeling; eval; test-time update|L1-L2|[](https://mirros-lab.github.io/code-as-world/)|
||Spatial-TTT|world models / test-time adaptation|world code; fast weights|environment modeling; eval; test-time update|L1-L2|[](https://arxiv.org/abs/2608.27549)|
|Wuya Zhiyuan\*|SHINE|continual / test-time learning|LoRA; skill vectors; weights|context adaptation; skill transfer|L1-L2|[](https://arxiv.org/abs/2602.06358)|
||LIFT|continual / test-time learning|LoRA; skill vectors; weights|context adaptation; skill transfer|L1-L2|[](https://arxiv.org/abs/2412.13626)|
||PaST|continual / test-time learning|LoRA; skill vectors; weights|context adaptation; skill transfer|L1-L2|[](https://arxiv.org/abs/2601.11258)|
|Singularity Escape / Nexus\*|Nexus|collaborative self-evolving agents|shared state; org knowledge; harness|collaboration; experience capture; harness adaptation|L3-L4 cand.|[](https://www.iimedia.cn/c1099/113820.html)|
|F. Persistent-memory & personal-AI companies  Cross-task memory, identity, or reusable skills are the main substrate of adaptation.|
|Engram|Knowledge Cartridges|persistent enterprise memory|knowledge modules; memory|extract; store; retrieve; adapt|L1-L2 adj.|[](https://engram.com/blog/legal-agents-with-memory)|
|Lemon AI / Hexdo|LemonAI Evolving|local persistent agents|workspace; memory; experience library|web / files / code; persistence; reuse|L1-L2|[](https://github.com/hexdocom/lemonai)|
|EverMind|EverOS|agent memory / OS|long-term memory; skills|retrieve; skill forge; active tasks; eval|L2-L3|[](https://github.com/EverMind-AI/EverOS)|
||Raven|agent memory / OS|long-term memory; skills|retrieve; skill forge; active tasks; eval|L2-L3|[](https://github.com/EverMind-AI/Raven)|
||EverMemOS|agent memory / OS|long-term memory; skills|retrieve; skill forge; active tasks; eval|L2-L3|[](https://arxiv.org/abs/2601.02163)|
|Mindverse|Second Me|personal memory / adaptation|identity model; memory; LoRA|memory modeling; personalization; retrieval|L1-L2|[](https://github.com/Mindverse/Second-Me)|
||Me.bot|personal memory / adaptation|identity model; memory; LoRA|memory modeling; personalization; retrieval|L1-L2|[](https://www.mindverse.com/about-us.html)|
