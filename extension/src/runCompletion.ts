import { Position, Range, TextDocument, WorkspaceConfiguration, workspace, window, env, Uri } from "vscode";
import { URL } from "url";
import * as vscode from 'vscode';
import fetch from "node-fetch";
import { AutocompleteResult, ResultEntry } from "./binary/requests/requests";
import { CHAR_LIMIT, FULL_BRAND_REPRESENTATION } from "./globals/consts";
import languages from "./globals/languages";
import { setDefaultStatus, setLoadingStatus } from "./statusBar/statusBar";
import { logInput, logOutput } from "./outputChannels";
import { getTabnineExtensionContext } from "./globals/tabnineExtensionContext";

export type CompletionType = "normal" | "snippet";

let didShowTokenWarning = false;

export default async function runCompletion(
  document: TextDocument,
  position: Position,
  timeout?: number,
  currentSuggestionText = ""
): Promise<AutocompleteResult | null | undefined> {
  setLoadingStatus(FULL_BRAND_REPRESENTATION);
  const offset = document.offsetAt(position);
  const beforeStartOffset = Math.max(0, offset - CHAR_LIMIT);
  const afterEndOffset = offset + CHAR_LIMIT;
  const beforeStart = document.positionAt(beforeStartOffset);
  const afterEnd = document.positionAt(afterEndOffset);
  const prefix = document.getText(new Range(beforeStart, position)) + currentSuggestionText;
  const suffix = document.getText(new Range(position, afterEnd));

  type Config = WorkspaceConfiguration & {
    enbale: boolean;
    modelIdOrEndpoint: string;
    isFillMode: boolean;
    startToken: string;
    middleToken: string;
    endToken: string;
    stopToken: string;
    temperature: number;
    maxTimeOut: number;
    maxNewTokens: number;
  };
  const config: Config = workspace.getConfiguration("StarCoderZZ") as Config;
  const { enbale, modelIdOrEndpoint, startToken, middleToken, endToken, stopToken, temperature, maxTimeOut, maxNewTokens } = config;

  // const context = getTabnineExtensionContext();
  // const apiToken = await context?.secrets.get("apiToken");

  if (!enbale) {
    setDefaultStatus();
    return null;
  }

  let endpoint = ""
  try {
    new URL(modelIdOrEndpoint);
    endpoint = modelIdOrEndpoint;
  } catch (e) {
    endpoint = `http://localhost:8000`;
    // if user hasn't supplied API Token yet, ask user to supply one
    // if (!apiToken && !didShowTokenWarning) {
    if (!didShowTokenWarning) {
      didShowTokenWarning = true;
      // void window.showInformationMessage(`In order to use "${modelIdOrEndpoint}" through Hugging Face API Inference, you'd need Hugging Face API Token`,
      //   "Get your token"
      // ).
      void window.showInformationMessage(`You are running StarCoderZZ for the first time, please set your API Endpoint`,
        "Set Endpoint"
      ).then(clicked => {
        if (clicked) {
          // open setting of extension config modelIdOrEndpoint 
          vscode.commands.executeCommand('workbench.action.openSettings', 'StarCoderZZ.modelIdOrEndpoint');
          // void env.openExternal(Uri.parse("https://github.com/huggingface/huggingface-vscode#hf-api-token"));
        }
      });
    }
  }

  // use FIM (fill-in-middle) mode if suffix is available
  const inputs = suffix.trim() ? `${startToken}${prefix}${endToken}${suffix}${middleToken}` : prefix;

  const data = {
    inputs,
    parameters: {
      max_new_tokens: maxNewTokens,
      temperature,
      do_sample: temperature > 0,
      top_p: 0.95,
      stop: [stopToken],
      max_time: maxTimeOut,
    }
  };

  logInput(inputs, data.parameters);

  const headers = {
    "Content-Type": "application/json",
    "Authorization": "",
  };
  // if (apiToken) {
  //   headers.Authorization = `Bearer ${apiToken}`;
  // }
  let code_completion_endpoint = endpoint + "/code/completion";
  const res = await fetch(code_completion_endpoint, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    console.error("Error sending a request", res.status, res.statusText);
    setDefaultStatus();
    return null;
  }

  const generatedTextRaw = getGeneratedText(await res.json());

  let generatedText = generatedTextRaw;
  if (generatedText.slice(0, inputs.length) === inputs) {
    generatedText = generatedText.slice(inputs.length);
  }
  generatedText = generatedText.replace(stopToken, "").replace(middleToken, "");

  const resultEntry: ResultEntry = {
    new_prefix: generatedText,
    old_suffix: "",
    new_suffix: ""
  }

  const result: AutocompleteResult = {
    results: [resultEntry],
    old_prefix: "",
    user_message: [],
    is_locked: false,
  }

  setDefaultStatus();
  logOutput(generatedTextRaw);
  return result;
}

function getGeneratedText(json: any): string {
  return json?.generated_text ?? json?.[0].generated_text ?? "";
}

export type KnownLanguageType = keyof typeof languages;

export function getLanguageFileExtension(
  languageId: string
): string | undefined {
  return languages[languageId as KnownLanguageType];
}

export function getFileNameWithExtension(document: TextDocument): string {
  const { languageId, fileName } = document;
  if (!document.isUntitled) {
    return fileName;
  }
  const extension = getLanguageFileExtension(languageId);
  if (extension) {
    return fileName.concat(extension);
  }
  return fileName;
}
