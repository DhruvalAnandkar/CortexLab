/**
 * Project Workspace Page
 * 
 * Main workspace for a research project with chat, agent timeline, and artifacts.
 */

import { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import {
    Send,
    Sparkles,
    FileText,
    Upload,
    Loader2,
    Download,
} from 'lucide-react';
import {
    projectsApi,
    messagesApi,
    runsApi,
    artifactsApi,
    type Message,
    type Artifact,
} from '../lib/api';
import { cn, formatRelativeTime, downloadBlob } from '../lib/utils';

export function ProjectWorkspace() {
    const { projectId } = useParams<{ projectId: string }>();
    const [message, setMessage] = useState('');
    const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const queryClient = useQueryClient();

    // Fetch project details
    const { data: project } = useQuery({
        queryKey: ['project', projectId],
        queryFn: () => projectsApi.get(projectId!).then((res) => res.data),
        enabled: !!projectId,
    });

    // Fetch messages
    const { data: messages = [] } = useQuery({
        queryKey: ['messages', projectId],
        queryFn: () => messagesApi.list(projectId!).then((res) => res.data),
        enabled: !!projectId,
        refetchInterval: 5000, // Poll for new messages
    });

    // Fetch artifacts
    const { data: artifactsData } = useQuery({
        queryKey: ['artifacts', projectId],
        queryFn: () => artifactsApi.list(projectId!).then((res) => res.data),
        enabled: !!projectId,
    });

    // Fetch runs
    const { data: runsData } = useQuery({
        queryKey: ['runs', projectId],
        queryFn: () => runsApi.list(projectId!).then((res) => res.data),
        enabled: !!projectId,
        refetchInterval: 3000,
    });

    // Send message mutation
    const sendMessageMutation = useMutation({
        mutationFn: (content: string) => messagesApi.send(projectId!, content, true),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['messages', projectId] });
            setMessage('');
        },
    });

    // Start discovery mutation
    const startDiscoveryMutation = useMutation({
        mutationFn: (query: string) => runsApi.startDiscovery(projectId!, query),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['runs', projectId] });
        },
    });

    // Scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        if (message.trim()) {
            sendMessageMutation.mutate(message.trim());
            startDiscoveryMutation.mutate(message.trim());
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleExportDocx = async (artifactId: string, title: string) => {
        try {
            const response = await artifactsApi.exportDocx(artifactId);
            downloadBlob(response.data, `${title}.docx`);
        } catch (error) {
            console.error('Export failed:', error);
        }
    };

    const currentRun = runsData?.runs.find((r) => r.status === 'running' || r.status === 'pending');

    return (
        <div className="flex h-[calc(100vh-64px)]">
            {/* Left Sidebar - Artifacts & Sources */}
            <div className="w-72 border-r border-[var(--color-border)] p-4 overflow-y-auto">
                <div className="space-y-6">
                    {/* Artifacts Section */}
                    <div>
                        <h3 className="text-sm font-semibold text-[var(--color-text-secondary)] uppercase tracking-wide mb-3">
                            Artifacts
                        </h3>
                        {artifactsData?.artifacts.length === 0 ? (
                            <p className="text-sm text-[var(--color-text-muted)]">
                                No artifacts yet. Start a research query to generate reports.
                            </p>
                        ) : (
                            <div className="space-y-2">
                                {artifactsData?.artifacts.map((artifact) => (
                                    <button
                                        key={artifact.id}
                                        onClick={() => setSelectedArtifact(artifact)}
                                        className={cn(
                                            "w-full text-left p-3 rounded-lg transition-all",
                                            selectedArtifact?.id === artifact.id
                                                ? "bg-[var(--color-primary)]/20 border border-[var(--color-primary)]"
                                                : "hover:bg-[var(--color-bg-tertiary)] border border-transparent"
                                        )}
                                    >
                                        <div className="flex items-center gap-2">
                                            <FileText className="w-4 h-4 text-[var(--color-primary)]" />
                                            <span className="text-sm font-medium truncate">
                                                {artifact.title}
                                            </span>
                                        </div>
                                        <p className="text-xs text-[var(--color-text-muted)] mt-1">
                                            {artifact.artifact_type} • v{artifact.version}
                                        </p>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Upload Section */}
                    <div>
                        <h3 className="text-sm font-semibold text-[var(--color-text-secondary)] uppercase tracking-wide mb-3">
                            Experiments
                        </h3>
                        <button className="w-full btn btn-secondary text-sm">
                            <Upload className="w-4 h-4" />
                            Upload Results
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Project Header */}
                <div className="border-b border-[var(--color-border)] p-4">
                    <h2 className="text-xl font-semibold">{project?.title || 'Loading...'}</h2>
                    {project?.description && (
                        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
                            {project.description}
                        </p>
                    )}
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.length === 0 ? (
                        <WelcomeMessage />
                    ) : (
                        messages.map((msg) => (
                            <MessageBubble key={msg.id} message={msg} />
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Agent Status */}
                {currentRun && (
                    <div className="border-t border-[var(--color-border)] p-3 bg-[var(--color-bg-secondary)]">
                        <div className="flex items-center gap-3">
                            <Loader2 className="w-5 h-5 text-[var(--color-primary)] animate-spin" />
                            <div>
                                <p className="text-sm font-medium">
                                    Agent is working on {currentRun.run_type.replace('_', ' ')}...
                                </p>
                                <p className="text-xs text-[var(--color-text-muted)]">
                                    This may take a few minutes
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Input Area */}
                <div className="border-t border-[var(--color-border)] p-4">
                    <div className="flex gap-3">
                        <input
                            type="text"
                            className="input flex-1"
                            placeholder="Describe your research area... (e.g., Computer Vision classifiers for medical imaging)"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={sendMessageMutation.isPending}
                        />
                        <button
                            onClick={handleSend}
                            disabled={!message.trim() || sendMessageMutation.isPending}
                            className="btn btn-primary disabled:opacity-50"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Right Panel - Artifact Viewer */}
            {selectedArtifact && (
                <div className="w-[500px] border-l border-[var(--color-border)] flex flex-col">
                    <div className="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
                        <div>
                            <h3 className="font-semibold">{selectedArtifact.title}</h3>
                            <p className="text-xs text-[var(--color-text-muted)]">
                                Version {selectedArtifact.version} • {formatRelativeTime(selectedArtifact.updated_at)}
                            </p>
                        </div>
                        <button
                            onClick={() => handleExportDocx(selectedArtifact.id, selectedArtifact.title)}
                            className="btn btn-secondary text-sm"
                        >
                            <Download className="w-4 h-4" />
                            Export
                        </button>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4">
                        <div className="markdown-content prose prose-invert max-w-none">
                            <ReactMarkdown>{selectedArtifact.content_markdown}</ReactMarkdown>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function MessageBubble({ message }: { message: Message }) {
    const isUser = message.role === 'user';

    return (
        <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
            <div
                className={cn(
                    "max-w-[80%] rounded-2xl px-4 py-3",
                    isUser
                        ? "bg-[var(--color-primary)] text-white rounded-br-sm"
                        : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-primary)] rounded-bl-sm"
                )}
            >
                {message.role === 'agent' && (
                    <div className="flex items-center gap-2 mb-2 text-[var(--color-primary)]">
                        <Sparkles className="w-4 h-4" />
                        <span className="text-xs font-medium">Research Agent</span>
                    </div>
                )}
                <div className="markdown-content text-sm">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
            </div>
        </div>
    );
}

function WelcomeMessage() {
    return (
        <div className="text-center py-12 space-y-6">
            <div className="w-16 h-16 mx-auto rounded-2xl gradient-bg flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-white" />
            </div>
            <div>
                <h3 className="text-xl font-semibold mb-2">Ready to explore?</h3>
                <p className="text-[var(--color-text-secondary)] max-w-md mx-auto">
                    Tell me about your research area and I'll help you discover gaps,
                    plan experiments, and draft your paper.
                </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
                {[
                    'Computer Vision classifiers',
                    'NLP for healthcare',
                    'Reinforcement learning',
                    'Graph neural networks',
                ].map((suggestion) => (
                    <button
                        key={suggestion}
                        className="btn btn-secondary text-sm"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        </div>
    );
}
