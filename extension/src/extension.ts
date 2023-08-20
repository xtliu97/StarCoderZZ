import * as vscode from "vscode";
import { registerCommands } from "./commandsHandler";
import tabnineExtensionProperties from "./globals/tabnineExtensionProperties";
import {
  COMPLETION_IMPORTS,
  handleImports,
  HANDLE_IMPORTS,
  getSelectionHandler,
} from "./selectionHandler";
import { registerStatusBar, setDefaultStatus } from "./statusBar/statusBar";
import { setTabnineExtensionContext } from "./globals/tabnineExtensionContext";
import installAutocomplete from "./autocompleteInstaller";
import handlePluginInstalled from "./handlePluginInstalled";

export async function activate(
  context: vscode.ExtensionContext
): Promise<void> {
  void initStartup(context);
  handleSelection(context);

  registerStatusBar(context);

  // Do not await on this function as we do not want VSCode to wait for it to finish
  // before considering TabNine ready to operate.
  void backgroundInit(context);

  if (context.extensionMode !== vscode.ExtensionMode.Test) {
    handlePluginInstalled(context);
  }

  const provider = new GPTProvider(context.extensionUri);
  console.log(context.extensionUri);
  // Put configuration settings into the provider

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      GPTProvider.viewType, provider, {
        webviewOptions: {
          retainContextWhenHidden: true,
        },
      }
    )
  );

  return Promise.resolve();
}

function initStartup(context: vscode.ExtensionContext): void {
  setTabnineExtensionContext(context);
}

async function backgroundInit(context: vscode.ExtensionContext) {
  setDefaultStatus();
  void registerCommands(context);

  await installAutocomplete(context);
}

export async function deactivate(){
}

function handleSelection(context: vscode.ExtensionContext) {
  if (tabnineExtensionProperties.isTabNineAutoImportEnabled) {
    context.subscriptions.push(
      vscode.commands.registerTextEditorCommand(
        COMPLETION_IMPORTS,
        getSelectionHandler(context)
      ),
      vscode.commands.registerTextEditorCommand(HANDLE_IMPORTS, handleImports)
    );
  }
}


class GPTProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'StarCoderZZ.chat';

	private _view?: vscode.WebviewView;

  	public selectedInsideCodeblock = false;

	public pasteOnClick = true;

	public keepConversation = true;

	public timeoutLength = 60;

  	constructor(private readonly extensionUri: vscode.Uri) {
		
	}

  
    private getHtmlForWebview(webview: vscode.Webview) {

		const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'main.js'));
		const microlightUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'scripts', 'microlight.min.js'));
		const tailwindUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'scripts', 'showdown.min.js'));
		const showdownUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'scripts', 'tailwind.min.js'));

		return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<script src="${tailwindUri}"></script>
				<script src="${showdownUri}"></script>
				<script src="${microlightUri}"></script>
				<style>
				.code {
					white-space : pre;
				</style>
			</head>
			<body>
				<input class="h-10 w-full text-white bg-stone-700 p-4 text-sm" type="text" id="prompt-input" />

				<div id="response" class="pt-6 text-sm">
				</div>

				<script src="${scriptUri}"></script>
			</body>
			</html>`;
	}

	public revive(panel: vscode.WebviewView) {
		this._view = panel;
	  }

    public resolveWebviewView(
		webviewView: vscode.WebviewView,
		context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken,
	) {

		this._view = webviewView;

		// set options for the webview
		webviewView.webview.options = {
			// Allow scripts in the webview
			enableScripts: true,
			localResourceRoots: [
				this.extensionUri
			]
		};

		// set the HTML for the webview
		webviewView.webview.html = this.getHtmlForWebview(webviewView.webview);

		
	}


  
}