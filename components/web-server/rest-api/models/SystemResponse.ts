/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface SystemResponse
 */
export interface SystemResponse {
    /**
     * 
     * @type {string}
     * @memberof SystemResponse
     */
    name: string;
    /**
     * 
     * @type {number}
     * @memberof SystemResponse
     */
    id: number;
}

/**
 * Check if a given object implements the SystemResponse interface.
 */
export function instanceOfSystemResponse(value: object): value is SystemResponse {
    if (!('name' in value) || value['name'] === undefined) return false;
    if (!('id' in value) || value['id'] === undefined) return false;
    return true;
}

export function SystemResponseFromJSON(json: any): SystemResponse {
    return SystemResponseFromJSONTyped(json, false);
}

export function SystemResponseFromJSONTyped(json: any, ignoreDiscriminator: boolean): SystemResponse {
    if (json == null) {
        return json;
    }
    return {
        
        'name': json['name'],
        'id': json['id'],
    };
}

export function SystemResponseToJSON(json: any): SystemResponse {
    return SystemResponseToJSONTyped(json, false);
}

export function SystemResponseToJSONTyped(value?: SystemResponse | null, ignoreDiscriminator: boolean = false): any {
    if (value == null) {
        return value;
    }

    return {
        
        'name': value['name'],
        'id': value['id'],
    };
}

